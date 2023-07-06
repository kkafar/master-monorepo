import polars as pl
import matplotlib.pyplot as plt


def plot_fitness_improvements(data: pl.DataFrame, plot: plt.Axes):
    data = (
        data
        .lazy()
        .filter(pl.col('event') == 'bestingen')
        .sort('gen')
        .collect()
    )

    print(data)
    x_data = data.get_column('gen')
    y_data = data.get_column('fitness')

    plot.plot(x_data, y_data, marker='o', linestyle='--')

