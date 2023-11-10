import polars as pl
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Optional
from .model import Col
from .filter import filter_sid
from .model import InstanceMetadata, JoinedExperimentData
from experiment.model import Experiment
from problem import Operation, JsspInstance


def create_plots_for_experiment(exp: Experiment, data: JoinedExperimentData, plotdir: Optional[Path]):
    # fig, plot = plt.subplots(nrows=1, ncols=1)
    # plot_best_in_gen(plot, data.bestingen, exp.instance)
    # plot.set(
    #     title=f"Best fitness by generation, {exp.name}, {exp.instance.jobs}j/{exp.instance.machines}m",
    #     xlabel="Generation",
    #     ylabel="Fitness value"
    # )
    # plot.legend()

    # fig, plot = plt.subplots(nrows=1, ncols=1)
    # plot_diversity(plot, data.popmetrics, exp.instance)
    # plot.set(
    #     title=f"Diversity rate by generation, {exp.name}, {exp.instance.jobs}j/{exp.instance.machines}m",
    #     xlabel="Generation",
    #     ylabel="Diversity rate"
    # )
    # plot.legend()

    fig_popmet, axes = plt.subplots(nrows=1, ncols=2)
    plot_diversity_avg(axes[0], data.popmetrics, exp.instance)
    if Col.DISTANCE in data.popmetrics.columns:  # Fix it by doing some kind of data-migration (insert empty column and rename files in old results)
        plot_distance_avg(axes[1], data.popmetrics, exp.instance)

    fig_bfavg, plot = plt.subplots(nrows=1, ncols=1)
    plot_best_in_gen_agg(plot, data.bestingen, exp.instance)

    if plotdir is not None:
        fig_popmet.tight_layout()
        fig_bfavg.tight_layout()
        fig_popmet.savefig(plotdir.joinpath(f'{exp.name}_pop_met.png'), dpi='figure', format='png')
        fig_bfavg.savefig(plotdir.joinpath(f'{exp.name}_fit_avg.png'), dpi='figure', format='png')
    plt.close(fig_popmet)
    plt.close(fig_bfavg)

    # plt.show()


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

    plot.errorbar(x_data, y_avg_data, yerr=y_std_data, label='Avg. diversity', linestyle='', marker='*', elinewidth=0.1)
    plot.set(
        title=f"Average diversity rate by generation, {metadata.id}, {metadata.jobs}j/{metadata.machines}m",
        xlabel="Generation",
        ylabel="Avgerage diversity rate"
    )
    plot.legend()


def plot_distance_avg(plot: plt.Axes, data: pl.DataFrame, metadata: InstanceMetadata):
    data_agg = (
        data.lazy()
        .group_by(pl.col(Col.GENERATION))
        .agg(
            pl.col(Col.DISTANCE).mean().alias('distance_avg'),
            pl.col(Col.DISTANCE).std().alias('distance_std')
        )
        .sort(pl.col(Col.GENERATION))
        .collect()
    )
    x_data = data_agg.get_column(Col.GENERATION)
    y_data = data_agg.get_column('distance_avg')
    yerr_data = data_agg.get_column('distance_std')

    plot.errorbar(x_data, y_data, yerr=yerr_data, linestyle='', marker='.', elinewidth=0.1)
    plot.set(
        title=f"Average average euc. dist. by generation, {metadata.id}, {metadata.jobs}j/{metadata.machines}m",
        xlabel="Generation",
        ylabel="Avgerage euc. dist."
    )
    plot.legend()


def plot_column_by_generation(plot: plt.Axes, data: pl.DataFrame, column_name: str):
    """ Expects `data` to be filtered data for single event type and column name to exists in `data.columns`.
        Also expects `Col.GENERATION` to exist in `data.columns` """
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

    plot.errorbar(x_data, y_avg_data, yerr=y_std_data, label='Avg. best fitness', linestyle='', marker='*', elinewidth=0.1)

    if metadata and metadata.best_solution:
        plot.plot(x_data, [metadata.best_solution for _ in range(len(x_data))], label='Best known sol.')

    plot.set(
        title=f"Average best fitness by generation, {metadata.id}, {metadata.jobs}j/{metadata.machines}m",
        xlabel="Generation",
        ylabel="Average best fitness"
    )
    plot.legend()


def plot_perf_cmp(dfbase: pl.DataFrame, dfbench: pl.DataFrame):
    pass


def visualise_instance_solution(exp: Experiment, instance: JsspInstance, series_id: int, plotdir: Optional[Path]):
    fig, plot = plt.subplots(nrows=1, ncols=1)

    for job in instance.jobs[1:]:
        x_ranges = []
        y_data = []
        for op in job.ops:
            y_data.extend([op.machine for _ in range(op.finish_time - op.duration, op.finish_time)])
            x_ranges.extend(range(op.finish_time - op.duration, op.finish_time))

        plt.scatter(x_ranges, y_data, label=f'Job {op.job_id}')

    plot.set_ylim(bottom=-1, top=instance.n_machines)
    plot.set_yticks(range(0, instance.n_machines))
    plot.set(
        title=f"{exp.name} solution, series: {series_id}, {exp.instance.jobs}j/{exp.instance.machines}m",
        xlabel="Time",
        ylabel="Machine"
    )
    plot.legend()
    plot.grid()

    if plotdir is not None:
        fig.savefig(plotdir.joinpath(f'{exp.name}_sol_{series_id}.png'), dpi='figure', format='png')
    else:
        plt.show()
    plt.close(fig)

