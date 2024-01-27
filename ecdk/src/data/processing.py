import polars as pl
import polars.selectors as cs
import itertools as it
from pathlib import Path
from typing import Optional
from experiment.model import Experiment
from data.model import JoinedExperimentData
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


def process_experiment_data(exp: Experiment, data: JoinedExperimentData, outdir: Optional[Path], should_plot: bool = True):
    """ :param outdir: directory for saving processed data """

    print(f"Processing experiment {exp.name}")

    exp_plotdir = get_plotdir_for_exp(exp, outdir) if outdir is not None else None

    instance = JsspInstance.from_instance_file(exp.config.input_file)
    for sid, series_output in enumerate(exp.result.series_outputs):
        md = series_output.data.metadata
        print(f"\tProcessing series {sid}: ")
        ok, schedule, errstr = validate_solution_string_in_context_of_instance(md.solution_string, instance, md.fitness)

        # if ok:
        #     print('OK')
        # else:
        #     print(f'ERR ({errstr})')

        if should_plot:
            visualise_instance_solution(exp, instance, sid, exp_plotdir)
        instance.reset()

    if should_plot:
        create_plots_for_experiment(exp, data, exp_plotdir)
    # compute_per_exp_stats(exp, data)


def process_experiment_batch_output(batch: list[Experiment], outdir: Optional[Path], process_count: int = 1, should_plot: bool = True):
    """ :param outdir: directory for saving processed data """

    data: list[JoinedExperimentData] = [experiment_data_from_all_series(exp) for exp in batch]

    # if process_count == 1:
    #     for exp, expdata in zip(batch, data):
    #         process_experiment_data(exp, expdata, outdir, should_plot)
    # else:
    #     from multiprocessing import get_context
    #     with get_context("spawn").Pool(process_count) as pool:
    #         pool.starmap(process_experiment_data, zip(batch, data, it.repeat(outdir), it.repeat(should_plot)))
    #
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

        # joined_df = exp_conv_df_1.vstack(exp_conv_df_2)

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

