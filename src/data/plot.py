import polars as pl
import matplotlib.pyplot as plt
from .model import Col
from .filter import filter_sid


def plot_best_in_gen(data: pl.DataFrame, plot: plt.Axes):
    """ Expects rows in `data` to comply to schema for `Event.BEST_IN_GEN` """
    plot_column_by_generation(data, plot, Col.FITNESS)


def plot_diversity(data: pl.DataFrame, plot: plt.Axes):
    """ Expects rows in `data` to comply to schema for `Event.DIVERSITY` """
    plot_column_by_generation(data, plot, Col.DIVERSITY)


def plot_column_by_generation(data: pl.DataFrame, plot: plt.Axes, column_name: str):
    """ Expects `data` to be filtered data for single event type and column name to exists in `data.columns`.
        Also expects `Col.GENERATION` to exist in `data.columns`."""
    series_ids = data.get_column(Col.SID).unique()
    for sid in series_ids:
        series_data = (
            data
            .lazy()
            .filter(filter_sid(sid))
            .sort(Col.GENERATION)
            .collect()
        )
        print(series_data)
        y_data = series_data.get_column(column_name)
        x_data = series_data.get_column(Col.GENERATION)
        plt.plot(x_data, y_data, marker='o', linestyle='--', label=f'Series {sid}')


def plot_iterinfo(data: pl.DataFrame, plot: plt.Axes):
    """ Expects rows in `data` to comply to schema for `Event.ITER_INFO` """
    sid = 0
    series_data = (
        data
        .lazy()
        .filter(filter_sid(sid))
        .sort(Col.GENERATION)
        .collect()
    )
    print(series_data)
    eval_time = series_data.get_column(Col.EVAL_TIME)
    cross_time = series_data.get_column(Col.CROSS_TIME)
    total_time = series_data.get_column(Col.ITER_TIME)
    x_data = series_data.get_column(Col.GENERATION)




    # Plot single bar here, take avg

    return None

