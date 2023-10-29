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


def compute_per_exp_stats(exp: Experiment, data: JoinedExperimentData, outdir: Optional[Path]):
    pass


def compute_global_exp_stats(batch: list[Experiment], data: list[JoinedExperimentData], outdir: Optional[Path]):

    fitness_avg_to_bks_dev_expr = (
        (pl.col(KEY_FITNESS_AVG) - pl.col(KEY_BKS)) / pl.col(KEY_BKS)
    )
    fitness_best_to_bks_dev_expr = (
        (pl.col(KEY_FITNESS_BEST) - pl.col(KEY_BKS)) / pl.col(KEY_BKS)
    )
    # bks_hitratio = (
    #     (pl.col())
    # )

    dfmain: pl.DataFrame | None = None

    for exp, expdata in zip(batch, data):
        df = (
            expdata.diversity.lazy()
            .select([
                pl.col(Col.DIVERSITY).mean().alias(KEY_DIV_AVG),
                pl.col(Col.DIVERSITY).std().alias(KEY_DIV_STD),
            ])
            .collect()
        )
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

        if dfmain is not None:
            dfmain.vstack(dfres, in_place=True)
        else:
            dfmain = dfres
        # break

    dfmain = (
        dfmain.lazy()
        .select([  # Column order, few columns are excluded: KEY_NSERIES
            KEY_EXPNAME, KEY_FITNESS_AVG, KEY_FITNESS_STD,
            KEY_FITNESS_BEST, KEY_BKS, KEY_FAVGTOBKS,
            KEY_FBTOBKS, KEY_DIV_AVG, KEY_DIV_STD,
            KEY_FITNESS_IMP_AVG, KEY_FITNESS_IMP_STD, KEY_BKS_HITRATIO
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
            'bks_hit_total': [bks_hit_in],
            'avg_dev_to_bks': [avg_dev_to_bks]
        }).write_csv(
            outdir.joinpath('summary_total.csv'),
            has_header=True,
            float_precision=2
        )


