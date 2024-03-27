import polars as pl
import polars.selectors as cs
import itertools as it
from tqdm import tqdm
from pprint import pprint
from pathlib import Path
from typing import Optional
from experiment.model import Experiment
from data.model import JoinedExperimentData, ExperimentValidationResult
from .tools import experiment_data_from_all_series
from .plot import create_plots_for_experiment, plot_perf_cmp, visualise_instance_solution
from .stat import (
    compute_per_exp_stats,
    compute_global_exp_stats,
    compare_perf_info,
    compute_convergence_iteration_per_exp
)
from core.fs import get_plotdir_for_exp, get_main_tabledir
from problem import (
    validate_solution_string_in_context_of_instance,
    JsspInstance
)


def process_experiment_data(exp: Experiment, data: JoinedExperimentData, outdir: Optional[Path], should_plot: bool = True) -> ExperimentValidationResult:
    """ :param outdir: directory for saving processed data """

    exp_plotdir = get_plotdir_for_exp(exp, outdir) if outdir is not None else None

    invalid_series = []

    instance = JsspInstance.from_instance_file(exp.config.input_file)
    for sid, series_output in enumerate(exp.result.series_outputs):
        md = series_output.data.metadata
        ok, schedule, errstr = validate_solution_string_in_context_of_instance(md.solution_string, instance, md.fitness)

        if not ok:
            invalid_series.append((sid, errstr))

        # if should_plot:
        #     visualise_instance_solution(exp, instance, sid, exp_plotdir)
        instance.reset()

    if should_plot:
        create_plots_for_experiment(exp, data, exp_plotdir)
    # compute_per_exp_stats(exp, data)

    return ExperimentValidationResult(exp.name, invalid_series if len(invalid_series) > 0 else None)


def process_experiment_batch_output(batch: list[Experiment], outdir: Optional[Path], process_count: int = 1, should_plot: bool = True):
    """ :param outdir: directory for saving processed data """

    print("Joining data from different series into single data frame...")
    data: list[JoinedExperimentData] = [experiment_data_from_all_series(exp) for exp in tqdm(batch)]

    validation_results: list[ExperimentValidationResult] = []
    has_corrupted_data = False

    if process_count == 1:
        print("Processing experiments data in single process...")
        for exp, expdata in tqdm(zip(batch, data), total=len(batch)):
            result = process_experiment_data(exp, expdata, outdir, should_plot)
            validation_results.append(result)
    else:
        print("Processing experiments data in multiprocess context...")
        from multiprocessing import get_context
        with get_context("spawn").Pool(process_count) as pool:
            validation_results = pool.starmap(process_experiment_data, tqdm(zip(batch, data, it.repeat(outdir), it.repeat(should_plot)), total=len(batch)))

    for result in filter(lambda res: not res.ok, validation_results):
        print(f"[ERROR] Experiment: {result.expname} has {len(result.corrupted_series)} corrupted series")
        pprint(result.corrupted_series)
        has_corrupted_data = True

    # As there are not mechanisms for handling (skipping during processing) corrupted data
    # it is best to just terminate processing.
    if has_corrupted_data:
        print("Validation: ERR")
        exit(1)
    else:
        print("Validation: OK")

    tabledir = get_main_tabledir(outdir) if outdir is not None else None
    global_df = compute_global_exp_stats(batch, data, tabledir)
    conv_df = compute_convergence_iteration_per_exp(batch, data, tabledir)

    if tabledir is not None:
        conv_df.write_csv(
            tabledir.joinpath('convergence_info.csv'),
            has_header=True,
            float_precision=2
        )


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

