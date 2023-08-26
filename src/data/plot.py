import polars as pl
import matplotlib.pyplot as plt
from .model import Col


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
            .filter(pl.col(Col.SID) == sid)
            .sort(Col.GENERATION)
            .collect()
        )
        print(series_data)
        y_data = series_data.get_column(column_name)
        x_data = series_data.get_column(Col.GENERATION)
        plt.plot(x_data, y_data, marker='o', linestyle='--', label=f'Series {sid}')

