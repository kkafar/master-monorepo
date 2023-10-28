from experiment.model import Experiment
from data.model import JoinedExperimentData
from .tools import experiment_data_from_all_series
from .plot import create_plots_for_experiment
from .stat import compute_per_exp_stats, compute_global_exp_stats


def process_experiment_data(exp: Experiment, data: JoinedExperimentData):
    print(f"Processing experiment {exp.name}")
    create_plots_for_experiment(exp, data)
    compute_per_exp_stats(exp, data)


def process_experiment_batch_output(batch: list[Experiment]):
    data = [experiment_data_from_all_series(exp) for exp in batch]

    for exp, expdata in zip(batch, data):
        process_experiment_data(exp, expdata)

    compute_global_exp_stats(batch, data)

