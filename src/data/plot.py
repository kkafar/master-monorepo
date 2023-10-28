import polars as pl
import matplotlib.pyplot as plt
from .model import Col
from .filter import filter_sid
from .model import InstanceMetadata, JoinedExperimentData
from experiment.model import Experiment


def create_plots_for_experiment(exp: Experiment, data: JoinedExperimentData):
    fig, plot = plt.subplots(nrows=1, ncols=1)
    plot_best_in_gen(plot, data.bestingen, exp.instance)
    plot.set(
        title=f"Best fitness by generation, {exp.name}, {exp.instance.jobs}j/{exp.instance.machines}m",
        xlabel="Generation",
        ylabel="Fitness value"
    )
    plot.legend()

    fig, plot = plt.subplots(nrows=1, ncols=1)
    plot_diversity(plot, data.diversity, exp.instance)
    plot.set(
        title=f"Diversity rate by generation, {exp.name}, {exp.instance.jobs}j/{exp.instance.machines}m",
        xlabel="Generation",
        ylabel="Diversity rate"
    )
    plot.legend()

    fig, plot = plt.subplots(nrows=1, ncols=1)
    plot_diversity_avg(plot, data.diversity, exp.instance)
    plot.set(
        title=f"Average diversity rate by generation, {exp.name}, {exp.instance.jobs}j/{exp.instance.machines}m",
        xlabel="Generation",
        ylabel="Avgerage diversity rate"
    )
    plot.legend()

    fig, plot = plt.subplots(nrows=1, ncols=1)
    plot_best_in_gen_agg(plot, data.bestingen, exp.instance)
    plot.set(
        title=f"Average best fitness by generation, {exp.name}, {exp.instance.jobs}j/{exp.instance.machines}m",
        xlabel="Generation",
        ylabel="Average best fitness"
    )
    plot.legend()

    plt.show()


def plot_best_in_gen(plot: plt.Axes, data: pl.DataFrame, metadata: InstanceMetadata):
    """ Expects rows in `data` to comply to schema for `Event.BEST_IN_GEN` """
    plot_column_by_generation(plot, data, Col.FITNESS)

    if metadata and metadata.best_solution:
        x_data = data.get_column(Col.GENERATION).unique().sort()
        plot.plot(x_data, [metadata.best_solution for _ in range(len(x_data))], label='Best known sol.')


def plot_diversity(plot: plt.Axes, data: pl.DataFrame, metadata: InstanceMetadata):
    """ Expects rows in `data` to comply to schema for `Event.DIVERSITY` """
    plot_column_by_generation(plot, data, Col.DIVERSITY)


def plot_diversity_avg(plot: plt.Axes, data: pl.DataFrame, metadata: InstanceMetadata):
    data_agg = (
        data.lazy()
        .groupby(pl.col(Col.GENERATION))
        .agg(
            pl.col(Col.DIVERSITY).mean().alias('diversity_avg'),
            pl.col(Col.DIVERSITY).std().alias('diversity_std')
        )
        .sort(pl.col(Col.GENERATION))
        .collect()
    )
    x_data = data_agg.get_column(Col.GENERATION)
    y_avg_data = data_agg.get_column('diversity_avg')
    y_std_data = data_agg.get_column('diversity_std')

    plot.errorbar(x_data, y_avg_data, yerr=y_std_data, label='Avg. diversity', linestyle='--', marker='*', elinewidth=1)


def plot_column_by_generation(plot: plt.Axes, data: pl.DataFrame, column_name: str):
    """ Expects `data` to be filtered data for single event type and column name to exists in `data.columns`.
        Also expects `Col.GENERATION` to exist in `data.columns`."""
    series_ids = data.get_column(Col.SID).unique()
    x_data = None
    for sid in series_ids:
        series_data = (
            data
            .lazy()
            .filter(filter_sid(sid))
            .sort(Col.GENERATION)
            .collect()
        )
        y_data = series_data.get_column(column_name)
        x_data = series_data.get_column(Col.GENERATION)
        plot.plot(x_data, y_data, marker='o', linestyle='--', label=f'Series {sid}')


def plot_best_in_gen_agg(plot: plt.Axes, data: pl.DataFrame, metadata: InstanceMetadata):
    data_agg = (
        data.lazy()
        .groupby(pl.col(Col.GENERATION))
        .agg(
            pl.col(Col.FITNESS).mean().alias('fitness_avg'),
            pl.col(Col.FITNESS).std().alias('fitness_std')
        )
        .sort(pl.col(Col.GENERATION))
        .collect()
    )

    x_data = data_agg.get_column(Col.GENERATION)
    y_avg_data = data_agg.get_column('fitness_avg')
    y_std_data = data_agg.get_column('fitness_std')

    plot.errorbar(x_data, y_avg_data, yerr=y_std_data, label='Avg. best fitness', linestyle='--', marker='*', elinewidth=1)

    if metadata and metadata.best_solution:
        plot.plot(x_data, [metadata.best_solution for _ in range(len(x_data))], label='Best known sol.')

