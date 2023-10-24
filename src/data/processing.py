import matplotlib.pyplot as plt
from experiment.model import Experiment
from data.model import JoinedExperimentData
from .tools import experiment_data_from_all_series
from .plot import (
    plot_diversity,
    plot_diversity_avg,
    plot_best_in_gen,
    plot_best_in_gen_agg,
)


def process_experiment_data(exp: Experiment, data: JoinedExperimentData):
    print(f"Processing experiment {exp.name}")

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


def process_experiment_batch_output(batch: list[Experiment]):
    for exp in batch:
        exp_data: JoinedExperimentData = experiment_data_from_all_series(exp)
        process_experiment_data(exp, exp_data)
