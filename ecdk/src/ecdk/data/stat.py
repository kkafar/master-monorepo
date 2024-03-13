import polars as pl
from pathlib import Path
from typing import Optional
from experiment.model import Experiment
from .model import JoinedExperimentData, Col

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


def compute_per_exp_stats(exp: Experiment, data: JoinedExperimentData, outdir: Optional[Path]):
    pass


def compute_global_exp_stats(batch: list[Experiment], data: list[JoinedExperimentData], outdir: Optional[Path]):
    fitness_avg_to_bks_dev_expr = (
        (pl.col(KEY_FITNESS_AVG) - pl.col(KEY_BKS)) / pl.col(KEY_BKS)
    )
    fitness_best_to_bks_dev_expr = (
        (pl.col(KEY_FITNESS_BEST) - pl.col(KEY_BKS)) / pl.col(KEY_BKS)
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
            .select((pl.col(KEY_FITNESS_BEST).count() / exp.config.n_series).alias('bks_hitratio'))
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
    )

    print(f'BKS found in {bks_hit_in} of {dfmain.height} cases ({(bks_hit_in * 100 / dfmain.height):.2f}%)')
    print(f'Avg. deviation to BKS {(avg_dev_to_bks * 100):.2f}%')

    if outdir is not None:
        dfmain.write_csv(
            outdir.joinpath('summary_by_exp.csv'),
            has_header=True,
            float_precision=2
        )

        pl.DataFrame({
            'n_instances': [dfmain.height],
            'bks_hit_total': [bks_hit_in],
            'avg_dev_to_bks': [avg_dev_to_bks]
        }).write_csv(
            outdir.joinpath('summary_total.csv'),
            has_header=True,
            float_precision=2
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

        # print(avg_cvg_iter)
        # print(n_converged)
        # break
    main_df = main_df.drop_nulls().sort(KEY_EXPNAME)
    print(main_df)

    return main_df



