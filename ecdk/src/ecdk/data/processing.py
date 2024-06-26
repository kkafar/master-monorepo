import polars as pl
import polars.selectors as cs
import itertools as it
import context
from tqdm import tqdm
from pathlib import Path
from typing import Optional, Generator, Iterable
from experiment.model import Experiment, Version, ExperimentId, SolutionHash
from data.model import JoinedExperimentData, ExperimentValidationResult, SeriesId
from .tools import experiment_data_from_all_series, extract_solver_desc_from_experiment_batch
from .plot import create_plots_for_experiment, plot_perf_cmp, visualise_instance_solution
from .stat import (
    compute_per_exp_stats,
    compute_global_exp_stats,
    compare_perf_info,
    compute_convergence_iteration_per_exp,
    compute_stats_from_solver_summary
)
from core.fs import get_plotdir_for_exp, get_main_tabledir, get_data_dir_from_ecdk_dir
from core.util import write_string_to_file
from problem import (
    validate_solution_string_in_context_of_instance,
    JsspInstance,
    ScheduleReconstructionResult,
)
from .constants import FLOAT_PRECISION
from .db.proxy import DatabaseProxy


DiffTableDesc = tuple[str, pl.DataFrame]


def validate_experiment_data(exp: Experiment, data: JoinedExperimentData, solver_version: Version) -> ExperimentValidationResult:
    """ Validates data of single experiment.

    :param exp: experiment with non-null result
    :param data: joined experiment data
    :returns: validation result with status & reconstructed schedules. The schedules are computed here
    as they are required for solution string validation anyway.
    """

    instance = JsspInstance.from_instance_file(exp.config.input_file)
    sol_reconstruction_results: list[ScheduleReconstructionResult] = []
    invalid_series: list[int] = []

    # TODO extract this to some external logic gates
    needs_numbering_translation = solver_version.major < 1

    for s_id, s_output in enumerate(exp.result.series_outputs):
        md = s_output.data.metadata
        result = validate_solution_string_in_context_of_instance(md.solution_string,
                                                                 instance,
                                                                 md.fitness,
                                                                 compat=needs_numbering_translation)
        sol_reconstruction_results.append(result)
        if not result.ok:
            invalid_series.append(s_id)

    invalid_series = invalid_series if len(invalid_series) > 0 else None
    return ExperimentValidationResult(exp.name, sol_reconstruction_results, invalid_series)


def validate_experiment_batch_data_gen(batch: list[Experiment],
                                       batch_data: list[JoinedExperimentData],
                                       solver_version: Version) -> Generator[ExperimentValidationResult, None, None]:
    return (validate_experiment_data(exp, exp_data, solver_version) for exp, exp_data in zip(batch, batch_data))


def validate_experiment_batch_data(batch: list[Experiment],
                                   batch_data: list[JoinedExperimentData],
                                   solver_version: Version,
                                   progress_bar: bool = False) -> list[ExperimentValidationResult]:
    if progress_bar:
        return list(tqdm(validate_experiment_batch_data_gen(batch, batch_data, solver_version), total=len(batch)))
    return list(validate_experiment_batch_data_gen(batch, batch_data, solver_version))


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

    print("Attempting to extract solver information from experiment batch...")
    solver_desc_res = extract_solver_desc_from_experiment_batch(batch)
    solver_version = Version(0, 1, 0)
    if solver_desc_res is not None:
        desc, json_str = solver_desc_res
        solver_version = desc.version
        print("Attempting to extract solver information from experiment batch OK")
    else:
        print("Attempting to extract solver information from experiment batch FAILED")

    print("Validating batch output...")

    # validation_results: Generator[ExperimentValidationResult, None, None] = validate_experiment_batch_data_gen(batch, data)
    validation_results: list[ExperimentValidationResult] = validate_experiment_batch_data(batch, data, solver_version=solver_version, progress_bar=True)
    has_corrupted_data = False

    for result in filter(lambda res: not res.ok, validation_results):
        print(f"[ERROR] Experiment: {result.expname} has {len(result.corrupted_series)} corrupted series")
        # pprint(list(map(lambda sid: (sid, result.reconstructed_schedules[sid]), result.corrupted_series)))
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

    print("Computing statistics...")
    run_metadata_stats_df = compute_stats_from_solver_summary(batch, data)
    global_df = compute_global_exp_stats(batch, data, tabledir)
    conv_df = compute_convergence_iteration_per_exp(batch, data, tabledir)

    if run_metadata_stats_df is not None:
        print("Looking for any previously unknown solutions...")
        ctx = context.get_context()
        db_proxy = DatabaseProxy(ctx.ecdk_db_path(), ctx.ecdk_instance_solutions_dir())
        look_for_new_solution(run_metadata_stats_df[1], db_proxy, tabledir)

    if tabledir is not None:
        print(f"Saving table data to {tabledir}...")
        conv_df.write_csv(
            tabledir.joinpath('convergence_info.csv'),
            has_header=True,
            float_precision=FLOAT_PRECISION
        )

        if run_metadata_stats_df:
            run_sum_df, sols_df = run_metadata_stats_df
            run_sum_df.write_csv(
                tabledir / 'run_summary_stats.csv',
                has_header=True,
                float_precision=FLOAT_PRECISION
            )
            sols_df.write_csv(
                tabledir / 'solutions.csv',
                has_header=True,
                float_precision=FLOAT_PRECISION
            )

    if outdir and solver_desc_res:
        solver_desc, json_str = solver_desc_res
        write_string_to_file(json_str, outdir / 'solver_desc.json')


def look_for_new_solution(hash_df: pl.DataFrame, db: DatabaseProxy, table_dir: Path = None) -> Iterable[tuple[ExperimentId, SolutionHash]]:
    """ :param hash_df: data frame with schema `expname, hash, fitness_best, series_id`
    """
    hash_series = hash_df.get_column("hash")
    unique_solutions = db.has_reference_solution_hashes(hash_series)
    new_solution_df_schema = {
        "experiment_id": pl.Utf8,
        "solution_hash": pl.Utf8,
        "series_id": pl.Int32,
    }
    new_solution_df = pl.DataFrame(schema=new_solution_df_schema)
    if len(unique_solutions) > 0:
        print("WOWOW, We've found a new solution(s)! Here they are:")
        series_ids = pl.Series("series_id", [hash_df.filter(pl.col("hash") == record[1])["sid"].item() for record in unique_solutions])
        experiment_ids = [t[0] for t in unique_solutions]
        solution_hashes = [t[1] for t in unique_solutions]
        new_solution_df = pl.DataFrame({
            "experiment_id": experiment_ids,
            "solution_hash": solution_hashes,
            "series_id": series_ids,
        }, schema=new_solution_df_schema)
        print(new_solution_df)
    else:
        print("No new previously unknown solutions found")

    if table_dir is not None:
        new_solution_df.write_csv(table_dir / 'discovered_solutions.csv', has_header=True)


def compare_exp_batch_outputs(basedir: Path, benchdir: Path):
    df_base = pl.read_csv(get_main_tabledir(basedir).joinpath('summary_by_exp.csv'), has_header=True)
    df_bench = pl.read_csv(get_main_tabledir(benchdir).joinpath('summary_by_exp.csv'), has_header=True)
    compare_perf_info(df_base, df_bench)
    plot_perf_cmp(df_base, df_bench)


def diff_numeric_columns(exp_dirs: list[Path], exp_dfs: list[pl.DataFrame]) -> Generator[DiffTableDesc, None, None]:
    for (exp_dir_1, exp_df_1), (exp_dir_2, exp_df_2) in it.combinations(zip(exp_dirs, exp_dfs), 2):
        if exp_dir_1 == exp_dir_2:
            continue

        print(exp_dir_1, exp_dir_2)

        exp_df_1 = exp_df_1.with_columns(pl.lit(pl.Series('batchname', [exp_dir_1.stem])))
        exp_df_2 = exp_df_2.with_columns(pl.lit(pl.Series('batchname', [exp_dir_2.stem])))

        numeric_cols = exp_df_1.select(cs.numeric()).columns

        joined_df = exp_df_1.join(exp_df_2, on='expname')
        stat_df = (joined_df.lazy()
                   .select([
                       pl.col('expname')
                   ] + [
                       (pl.col(col + '_right') - pl.col(col)).alias(col + '_diff')
                       for col in numeric_cols
                   ])
                   ).collect()

        # print(stat_df)
        # print(exp_dir_2.stem, '-', exp_dir_1.stem)

        table_name = f"{exp_dir_2.stem}-X-{exp_dir_1.stem}"
        yield (table_name, stat_df)


def diff_table_in_batch(exp_dirs: list[Path], table_name: str, outdir: Optional[Path] = None):
    table_name_w_suffix = table_name
    if not table_name_w_suffix.endswith('.csv'):
        table_name_w_suffix = table_name + '.csv'

    print(f"Loading {table_name} tables...")
    exp_dfs = [pl.read_csv(get_main_tabledir(exp_dir).joinpath(table_name_w_suffix), has_header=True)
               for exp_dir in tqdm(exp_dirs)]

    print(f"Processing {table_name} tables...")
    for (desc, table) in diff_numeric_columns(exp_dirs, exp_dfs):
        print(desc)
        print(table)

        table: pl.DataFrame = table

        if outdir is not None:
            savefile = f"{desc}-X-{table_name_w_suffix}"
            print(f"Saving to {savefile}")
            table.write_csv(outdir / savefile, include_header=True, float_precision=FLOAT_PRECISION)


def compare_processed_exps(exp_dirs: list[Path], outdir: Optional[Path] = None):
    diff_table_in_batch(exp_dirs, 'convergence_info', outdir)
    diff_table_in_batch(exp_dirs, 'summary_by_exp', outdir)
    # diff_table_in_batch(exp_dirs, 'summary_total', outdir)

