import polars as pl
from pathlib import Path
from typing import Optional
from experiment.model import Experiment
from .model import JoinedExperimentData, Col
from .constants import FLOAT_PRECISION

KEY_EXPNAME = 'expname'
KEY_FITNESS_AVG = 'fitness_avg'
KEY_FITNESS_STD = 'fitness_std'
KEY_FITNESS_BEST = 'fitness_best'
KEY_BKS = 'bks'
KEY_FAVGTOBKS = 'fitness_avg_to_bks_dev'
KEY_FBTOBKS = 'fitness_best_to_bks_dev'
KEY_DIV_AVG = 'diversity_avg'
KEY_DIV_STD = 'diversity_std'
KEY_FITNESS_IMP_AVG = 'fitness_n_improv_avg'  # avg n of fitness improvements
KEY_FITNESS_IMP_STD = 'fitness_n_improv_std'
KEY_NSERIES = 'n_series'
KEY_BKS_HITRATIO = 'bks_hitratio'  # fraction of series where bks was achieved
KEY_ITERTIME_AVG = 'itertime_avg'
KEY_ITERTIME_STD = 'itertime_std'

# Dataframe from run_metadata of each series
KEY_HASH = 'hash'  # hash of the solution in given series
KEY_TOTAL_TIME = 'total_time'  # total time of solver run in given series
KEY_TOTAL_TIME_AVG = 'total_time_avg'
KEY_TOTAL_TIME_STD = 'total_time_std'
KEY_BEST_HASH = 'best_hash'  # hash of best individual across all series
KEY_UNIQUE_SOLS = 'unique_sols'  # number of unique solutions across series
KEY_UNIQUE_SOLS_MAX = 'unique_sols_max'
KEY_UNIQUE_SOLS_AVG = 'unique_sols_avg'  # number of unique solutions across series
KEY_UNIQUE_SOLS_STD = 'unique_sols_std'  # number of unique solutions across series
KEY_AGE_MAX = 'age_max'  # max age of individual in given series / also used in summary across series context
KEY_AGE_AVG = 'age_avg'  # each series reports an average age of death of indv., this is average of this value across all series
KEY_AGE_STD = 'age_std'  # ^ look above ^ std of this value
KEY_INDV_COUNT = 'indv_count'  # number of different individuals in population across all generations in given series
KEY_INDV_COUNT_AVG = 'indiv_count_avg'  # aggregate of above ^ value
KEY_INDV_COUNT_STD = 'indiv_count_std'  # std of above ^ value
KEY_CROSSOVER_INV_MAX = 'co_inv_max'  # max of how many times a single indvidual took part in crossover in given series
KEY_CROSSOVER_INV_MIN = 'co_inv_min'  # min of how many times a single indvidual took part in crossover in given series


def compute_per_exp_stats(exp: Experiment, data: JoinedExperimentData, outdir: Optional[Path]):
    pass


def compute_global_exp_stats(batch: list[Experiment], data: list[JoinedExperimentData], outdir: Optional[Path]):
    fitness_avg_to_bks_dev_expr = (
        (pl.col(KEY_FITNESS_AVG) - pl.col(KEY_BKS)) / pl.col(KEY_BKS) * 100
    )
    fitness_best_to_bks_dev_expr = (
        (pl.col(KEY_FITNESS_BEST) - pl.col(KEY_BKS)) / pl.col(KEY_BKS) * 100
    )

    dfmain = pl.DataFrame()

    for exp, expdata in zip(batch, data):
        # Diversity stats
        df = (
            expdata.popmetrics.lazy()
            .select([
                pl.col(Col.DIVERSITY).mean().alias(KEY_DIV_AVG),
                pl.col(Col.DIVERSITY).std().alias(KEY_DIV_STD),
            ])
            .collect()
        )

        # Avg. number of improvements
        df = (
            expdata.newbest.lazy()
            .group_by(pl.col(Col.SID))
            .agg((pl.count() - 1).alias('count'))  # -1 because new_best is also reported from initial population
            .select([
                pl.col('count').mean().alias(KEY_FITNESS_IMP_AVG),
                pl.col('count').std().alias(KEY_FITNESS_IMP_STD)
            ])
            .collect()
            .hstack(df, in_place=True)  # stacking two smaller dframes here
        )

        # Iteration time stats
        df = (
            expdata.iterinfo.lazy()
            .select([
                pl.col(Col.ITER_TIME).mean().alias(KEY_ITERTIME_AVG),
                pl.col(Col.ITER_TIME).std().alias(KEY_ITERTIME_STD)
            ])
            .collect()
            .hstack(df, in_place=True)
        )
        dfbks_hitratio = (
            expdata.bestingen.lazy()
            .group_by(pl.col(Col.SID))
            .agg(pl.col(Col.FITNESS).min().alias(KEY_FITNESS_BEST))
            .filter(pl.col(KEY_FITNESS_BEST) == exp.instance.best_solution)
            .select((pl.col(KEY_FITNESS_BEST).count() * 100 / exp.config.n_series).alias('bks_hitratio'))
            .collect()
        )
        dfres = (
            expdata.bestingen.lazy()
            .select([
                pl.col(Col.FITNESS).mean().alias(KEY_FITNESS_AVG),
                pl.col(Col.FITNESS).std().alias(KEY_FITNESS_STD),
                pl.col(Col.FITNESS).min().alias(KEY_FITNESS_BEST),
            ])
            .with_columns([
                pl.Series(KEY_EXPNAME, [exp.name]),
                pl.Series(KEY_BKS, [exp.instance.best_solution]),
                pl.Series(KEY_NSERIES, [exp.config.n_series]),
                dfbks_hitratio.get_column(KEY_BKS_HITRATIO)
            ])
            .with_columns([
                fitness_avg_to_bks_dev_expr.alias(KEY_FAVGTOBKS),
                fitness_best_to_bks_dev_expr.alias(KEY_FBTOBKS)
            ])
            .collect()
            .hstack(df, in_place=True)
        )

        dfmain.vstack(dfres, in_place=True)
        # break

    dfmain = (
        dfmain.lazy()
        .select([  # Column order, few columns are excluded: KEY_NSERIES
            KEY_EXPNAME, KEY_FITNESS_AVG, KEY_FITNESS_STD,
            KEY_FITNESS_BEST, KEY_BKS, KEY_FAVGTOBKS,
            KEY_FBTOBKS, KEY_DIV_AVG, KEY_DIV_STD,
            KEY_FITNESS_IMP_AVG, KEY_FITNESS_IMP_STD, KEY_BKS_HITRATIO,
            KEY_ITERTIME_AVG, KEY_ITERTIME_STD
        ])
        .sort(KEY_EXPNAME)
        .collect()
    )

    print(dfmain.head(100))

    bks_hit_in = (
        dfmain
        .filter(pl.col(KEY_FITNESS_BEST) == pl.col(KEY_BKS))
        .height
    )

    avg_dev_to_bks = (
        dfmain.lazy()
        .select(pl.col(KEY_FBTOBKS).mean())
        .collect()
        .to_series()
        .item()
    )  # We do not multiply by 100 here, as the values are already in percents.

    print(f'BKS found in {bks_hit_in} of {dfmain.height} cases ({(bks_hit_in * 100 / dfmain.height):.2f}%)')
    print(f'Avg. deviation to BKS {avg_dev_to_bks:.2f}%')

    if outdir is not None:
        dfmain.write_csv(
            outdir.joinpath('summary_by_exp.csv'),
            has_header=True,
            float_precision=FLOAT_PRECISION
        )

        pl.DataFrame({
            'n_instances': [dfmain.height],
            'bks_hit_total': [bks_hit_in],
            'avg_dev_to_bks': [avg_dev_to_bks]
        }).write_csv(
            outdir.joinpath('summary_total.csv'),
            has_header=True,
            float_precision=FLOAT_PRECISION
        )

    return dfmain


def compare_perf_info(df_base: pl.DataFrame, df_bench: pl.DataFrame):
    expname_base = df_base.get_column(KEY_EXPNAME)
    expname_bench = df_bench.get_column(KEY_EXPNAME)
    assert (expname_base == expname_bench).all(), "Both compared batches must contain results for the same experiments & in the same order"

    s_base_it_avg = df_base.get_column(KEY_ITERTIME_AVG)
    s_bench_it_avg = df_bench.get_column(KEY_ITERTIME_AVG)

    df_res = pl.DataFrame({
        'expname': expname_base,
        'base_it_avg': s_base_it_avg,
        'base_it_std': df_base.get_column(KEY_ITERTIME_STD),
        'bench_it_avg': s_bench_it_avg,
        'bench_it_std': df_bench.get_column(KEY_ITERTIME_STD),
        'relative_imp': ((s_bench_it_avg - s_base_it_avg) / s_base_it_avg)
    })

    print(df_res)


def compute_convergence_iteration_per_exp(batch: list[Experiment], data: list[JoinedExperimentData], outdir: Optional[Path]) -> pl.DataFrame:
    main_df = pl.DataFrame()
    colgen = pl.col(Col.GENERATION)

    for exp, nb_df in zip(batch, map(lambda jd: jd.newbest, data)):
        nb_df: pl.DataFrame = nb_df
        # print(nb_df)
        nb_df = (nb_df.lazy()
                 .group_by(pl.col(Col.SID))
                 .agg([
                     pl.all().sort_by(colgen).last()
                 ])
                 .collect()
                 .sort(pl.col(Col.SID))
                 )

        n_series = nb_df.height

        # Assuming that best_solution exists here in the first place
        bks = exp.instance.best_solution

        converged_exps_df = nb_df.filter(pl.col(Col.FITNESS) == bks)
        pre400_df = converged_exps_df.filter(pl.col(Col.GENERATION) <= 400)

        n_converged = converged_exps_df.height
        avg_cvg_iter = (converged_exps_df
                        .select([
                            pl.lit(pl.Series(KEY_EXPNAME, (exp.name,))),
                            colgen.mean().alias('avg_cvg_iter'),
                            colgen.std().alias('std_cvg_iter'),
                            colgen.median().alias('median_cvg_iter'),
                            colgen.min().alias('min_cvg_iter'),
                            colgen.max().alias('max_cvg_iter'),
                            pl.lit(pl.Series(KEY_BKS_HITRATIO, (n_converged * 100 / n_series,))),
                            pl.lit(pl.Series('pre400_bks_hitratio', (pre400_df.height * 100 / n_series,)))
                        ])
                        )

        main_df.vstack(avg_cvg_iter, in_place=True)

    main_df = (
        main_df
        .filter(pl.col('avg_cvg_iter').is_not_null())
        .sort(KEY_EXPNAME)
        .with_columns((
            # Null values occur when there is only single data point
            pl.col('std_cvg_iter').fill_null(pl.lit(0))
        ))
    )
    print(main_df)
    return main_df


def compute_stats_from_solver_summary(
        batch: list[Experiment],
        data: list[JoinedExperimentData]) -> Optional[tuple[pl.DataFrame, pl.DataFrame]]:
    """ Computes statistics & extracts information based on solver summary (run_metadata.json).
    This function assumes that data & batch structures are synchronized (on index i there is data for ith experiment).

    :param batch: iterable of experiments
    :param data: joined data for respective batch experiments
    :return: tuple of two data frames - first one contains statistics, second one stores hashes & experiment_ids
    """
    main_df = pl.DataFrame()
    hash_df = pl.DataFrame()

    for exp, summary_df in zip(batch, map(lambda d: d.summarydf, data)):
        summary_df: pl.DataFrame = summary_df

        # As old data does not have data in certain columns we want to shortcircuit
        # and just don't compute these stats at all
        null_counts = summary_df.null_count().row(0)
        if any(map(lambda value: value > 0, null_counts)):
            return None

        # Desired table schema:
        #
        # KEY_AGE_AVG = 'age_avg'  # each series reports an average age of death of indv., this is average of this value across all series
        # KEY_AGE_STD = 'age_std'  # ^ look above ^ std of this value
        # KEY_UNIQUE_SOLS_MAX = 'unique_sols_max'
        # KEY_UNIQUE_SOLS_AVG = 'unique_sols_avg'  # number of unique solutions across series
        # KEY_UNIQUE_SOLS_STD = 'unique_sols_std'  # number of unique solutions across series
        # KEY_INDV_COUNT = 'indv_count'  # number of different individuals in population across all generations in given series
        # KEY_INDV_COUNT_AVG = 'indiv_count_avg'  # aggregate of above ^ value
        # KEY_INDV_COUNT_STD = 'indiv_count_std'  # std of above ^ value
        # KEY_CROSSOVER_INV_MAX = 'co_inv_max'  # max of how many times a single indvidual took part in crossover in given series
        # KEY_CROSSOVER_INV_MIN = 'co_inv_min'  # min of how many times a single indvidual took part in crossover in given series

        # This should be a separate table, as there might be multiple hashes with best fitness
        # KEY_BEST_HASH = 'best_hash'  # hash of best individual across all series

        # TODO: Think this through, maybe it would be better to split this into few separate tables
        new_df = (
            summary_df
            .lazy()
            .select([
                pl.lit(pl.Series(KEY_EXPNAME, (exp.name,))),
                pl.col(KEY_AGE_AVG).mean(),
                pl.col(KEY_AGE_AVG).std().alias(KEY_AGE_STD),
                pl.col(KEY_AGE_MAX).max(),
                pl.col(KEY_HASH).n_unique().alias(KEY_UNIQUE_SOLS),
                pl.col(KEY_INDV_COUNT).mean().alias(KEY_INDV_COUNT_AVG),
                pl.col(KEY_INDV_COUNT).std().alias(KEY_INDV_COUNT_STD),
                pl.col(KEY_CROSSOVER_INV_MAX).max(),
                pl.col(KEY_CROSSOVER_INV_MIN).min(),
                pl.col(Col.FITNESS).min().alias(KEY_FITNESS_BEST),
                pl.col(KEY_TOTAL_TIME).mean().alias(KEY_TOTAL_TIME_AVG),
                pl.col(KEY_TOTAL_TIME).std().alias(KEY_TOTAL_TIME_STD),
            ])
            .collect()
        )

        best_fitness = new_df.get_column(KEY_FITNESS_BEST).item()

        new_hash_df = (
            summary_df
            .lazy()
            .filter(pl.col(Col.FITNESS) == best_fitness)
            .group_by(pl.col(KEY_HASH))
            .agg(pl.col(Col.SID).min())  # We take smalest series id from unique ones
            .select([
                pl.lit(pl.Series(KEY_EXPNAME, (exp.name,))),
                pl.lit(pl.Series(KEY_FITNESS_BEST, (best_fitness,))),
                pl.all(),
            ])
            .collect()
        )

        main_df.vstack(new_df, in_place=True)
        hash_df.vstack(new_hash_df, in_place=True)

    main_df = main_df.sort(KEY_EXPNAME)
    hash_df = hash_df.sort(KEY_EXPNAME)

    print(main_df)
    print(hash_df)
    return main_df, hash_df

