import polars as pl
import matplotlib.pyplot as plt
from .model import Col


def plot_best_in_gen(data: pl.DataFrame, plot: plt.Axes):
    """ Expects rows in `data` to comply to schema for `Event.BEST_IN_GEN` """
    n_series = data.get_column(Col.SID).n_unique()
    for sid in range(n_series):
        series_data = (
            data
            .lazy()
            .filter(pl.col(Col.SID) == sid)
            .sort(Col.GENERATION)
            .collect()
        )
        print(series_data)
        y_data = series_data.get_column(Col.FITNESS)
        x_data = series_data.get_column(Col.GENERATION)
        plt.plot(x_data, y_data, marker='o', linestyle='--', label=f'Series {sid}')


def plot_diversity(data: pl.DataFrame, plot: plt.Axes):
    """ Expects rows in `data` to comply to schema for `Event.DIVERSITY` """
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
        y_data = series_data.get_column(Col.DIVERSITY)
        x_data = series_data.get_column(Col.GENERATION)
        plt.plot(x_data, y_data, marker='o', linestyle='--', label=f'Series {sid}')
