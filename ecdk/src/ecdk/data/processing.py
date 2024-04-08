import polars as pl
import polars.selectors as cs
import itertools as it
from tqdm import tqdm
from pprint import pprint
from pathlib import Path
from typing import Optional, Generator
from experiment.model import Experiment
from data.model import JoinedExperimentData, ExperimentValidationResult
from .tools import experiment_data_from_all_series, extract_solver_desc_from_experiment_batch
from .plot import create_plots_for_experiment, plot_perf_cmp, visualise_instance_solution
from .stat import (
    compute_per_exp_stats,
    compute_global_exp_stats,
    compare_perf_info,
    compute_convergence_iteration_per_exp,
    compute_stats_from_solver_summary
)
from core.fs import get_plotdir_for_exp, get_main_tabledir
from core.util import write_string_to_file
from problem import (
    validate_solution_string_in_context_of_instance,
    JsspInstance,
    ScheduleReconstructionResult,
)


def validate_experiment_data(exp: Experiment, data: JoinedExperimentData) -> ExperimentValidationResult:
    """ Validates data of single experiment.

    :param exp: experiment with non-null result
    :param data: joined experiment data
    :returns: validation result with status & reconstructed schedules. The schedules are computed here
    as they are required for solution string validation anyway.
    """

    instance = JsspInstance.from_instance_file(exp.config.input_file)
    sol_reconstruction_results: list[ScheduleReconstructionResult] = []
    invalid_series: list[int] = []

    for s_id, s_output in enumerate(exp.result.series_outputs):
        md = s_output.data.metadata
        result = validate_solution_string_in_context_of_instance(md.solution_string,
                                                                 instance,
                                                                 md.fitness)
        sol_reconstruction_results.append(result)
        if not result.ok:
            invalid_series.append(s_id)

    invalid_series = invalid_series if len(invalid_series) > 0 else None
    return ExperimentValidationResult(exp.name, sol_reconstruction_results, invalid_series)


def validate_experiment_batch_data_gen(batch: list[Experiment],
                                       batch_data: list[JoinedExperimentData]) -> Generator[ExperimentValidationResult, None, None]:
    return (validate_experiment_data(exp, exp_data) for exp, exp_data in zip(batch, batch_data))


def validate_experiment_batch_data(batch: list[Experiment],
                                   batch_data: list[JoinedExperimentData],
                                   progress_bar: bool = False) -> list[ExperimentValidationResult]:
    if progress_bar:
        return list(tqdm(validate_experiment_batch_data_gen(batch, batch_data), total=len(batch)))
    return list(validate_experiment_batch_data_gen(batch, batch_data))


def find_some_best_series(exp: Experiment) -> int:
    return min(range(len(exp.result.series_outputs)), key=lambda i: exp.result.series_outputs[i].data.metadata.fitness)


def process_experiment_data(exp: Experiment,
                            data: JoinedExperimentData,
                            validation_result: ExperimentValidationResult,
                            outdir: Optional[Path],
                            should_plot: bool = True):
    """ Main processing of per-exp data, expects validation_result to be OK """

    assert validation_result.ok, "Validation result must be OK in processing stage"

    if not should_plot:
        return

    exp_plotdir = get_plotdir_for_exp(exp, outdir) if outdir is not None else None

    some_best_series = find_some_best_series(exp)

    visualise_instance_solution(exp,
                                validation_result.reconstructed_schedules[some_best_series].instance,
                                some_best_series,
                                exp_plotdir)

    create_plots_for_experiment(exp, data, some_best_series, exp_plotdir)

    # compute_per_exp_stats(exp, data)


def process_experiment_batch_output(batch: list[Experiment], outdir: Optional[Path], process_count: int = 1, should_plot: bool = True):
    """ :param outdir: directory for saving processed data """

    print("Joining data from different series into single data frame...")
    data: list[JoinedExperimentData] = [experiment_data_from_all_series(exp) for exp in tqdm(batch)]

    print("Validating batch output...")

    # validation_results: Generator[ExperimentValidationResult, None, None] = validate_experiment_batch_data_gen(batch, data)
    validation_results: list[ExperimentValidationResult] = validate_experiment_batch_data(batch, data, progress_bar=True)
    has_corrupted_data = False

    for result in filter(lambda res: not res.ok, validation_results):
        print(f"[ERROR] Experiment: {result.expname} has {len(result.corrupted_series)} corrupted series")
        pprint(list(map(lambda sid: (sid, result.reconstructed_schedules[sid]))))
        has_corrupted_data = True

    # As there are not mechanisms for handling (skipping during processing) corrupted data
    # it is best to just terminate processing.
    if has_corrupted_data:
        print("[ERROR] Validation failed")
        exit(1)
    else:
        print("Validation finished successfully")

    if process_count == 1:
        print("Processing experiments data in single process...")
        for exp, expdata, valres in tqdm(zip(batch, data, validation_results), total=len(batch)):
            process_experiment_data(exp, expdata, valres, outdir, should_plot)
    else:
        print("Processing experiments data in multiprocess context...")
        from multiprocessing import get_context
        with get_context("spawn").Pool(process_count) as pool:
            pool.starmap(process_experiment_data,
                         tqdm(zip(batch,
                                  data,
                                  validation_results,
                                  it.repeat(outdir),
                                  it.repeat(should_plot)),
                              total=len(batch)))

    tabledir = get_main_tabledir(outdir) if outdir is not None else None

    solver_desc_res = extract_solver_desc_from_experiment_batch(batch)

    res_sum_df = compute_stats_from_solver_summary(batch, data)
    global_df = compute_global_exp_stats(batch, data, tabledir)
    conv_df = compute_convergence_iteration_per_exp(batch, data, tabledir)

    if tabledir is not None:
        conv_df.write_csv(
            tabledir.joinpath('convergence_info.csv'),
            has_header=True,
            float_precision=2
        )

        if res_sum_df:
            run_sum_df, sols_df = res_sum_df
            run_sum_df.write_csv(
                tabledir / 'run_summary_stats.csv',
                has_header=True,
                float_precision=2
            )
            sols_df.write_csv(
                tabledir / 'solutions.csv',
                has_header=True,
                float_precision=2
            )

    if outdir and solver_desc_res:
        solver_desc, json_str = solver_desc_res
        write_string_to_file(json_str, outdir / 'solver_desc.json')


def compare_exp_batch_outputs(basedir: Path, benchdir: Path):
    df_base = pl.read_csv(get_main_tabledir(basedir).joinpath('summary_by_exp.csv'), has_header=True)
    df_bench = pl.read_csv(get_main_tabledir(benchdir).joinpath('summary_by_exp.csv'), has_header=True)
    compare_perf_info(df_base, df_bench)
    plot_perf_cmp(df_base, df_bench)


def compare_processed_exps(exp_dirs: list[Path], outdir: Optional[Path]):
    exps_conv_info_df = [pl.read_csv(get_main_tabledir(exp_dir).joinpath('convergence_info.csv'), has_header=True)
                         for exp_dir in exp_dirs]

    for (exp_dir_1, exp_conv_df_1), (exp_dir_2, exp_conv_df_2) in it.combinations(zip(exp_dirs, exps_conv_info_df), 2):
        if exp_dir_1 == exp_dir_2:
            continue

        print(exp_dir_1, exp_dir_2)

        exp_conv_df_1 = exp_conv_df_1.with_columns(pl.lit(pl.Series('batchname', [exp_dir_1.stem])))
        exp_conv_df_2 = exp_conv_df_2.with_columns(pl.lit(pl.Series('batchname', [exp_dir_2.stem])))

        numeric_cols = exp_conv_df_1.select(cs.numeric()).columns

        joined_df = exp_conv_df_1.join(exp_conv_df_2, on='expname')
        stat_df = (joined_df.lazy()
                   .select([
                       pl.col('expname')
                   ] + [
                       (pl.col(col + '_right') - pl.col(col)).alias(col + '_diff')
                       for col in numeric_cols
                   ])
                   ).collect()

        print(stat_df)
        print(exp_dir_2.stem, '-', exp_dir_1.stem)

