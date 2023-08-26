import polars as pl
import matplotlib.pyplot as plt
from data.model import Col, Event


def plot_fitness_improvements(data: pl.DataFrame, plot: plt.Axes):
    data = (
        data
        .lazy()
        .filter(pl.col(Col.EVENT) == Event.BEST_IN_GEN)
        .sort(Col.GENERATION)
        .collect()
    )

    x_data = data.get_column(Col.GENERATION)
    y_data = data.get_column(Col.GENERATION)

    plot.plot(x_data, y_data, marker='o', linestyle='--')

