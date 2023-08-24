import polars as pl
import matplotlib.pyplot as plt
from model import COL_EVENT, EVENT_BEST_IN_GEN, COL_GENERATION, COL_FITNESS


def plot_fitness_improvements(data: pl.DataFrame, plot: plt.Axes):
    data = (
        data
        .lazy()
        .filter(pl.col(COL_EVENT) == EVENT_BEST_IN_GEN)
        .sort(COL_GENERATION)
        .collect()
    )

    x_data = data.get_column(COL_GENERATION)
    y_data = data.get_column(COL_FITNESS)

    plot.plot(x_data, y_data, marker='o', linestyle='--')

