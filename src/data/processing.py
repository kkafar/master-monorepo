from experiment.model import Experiment
from data.model import JoinedExperimentData
from .tools import experiment_data_from_all_series
from .plot import create_plots_for_experiment


def process_experiment_data(exp: Experiment, data: JoinedExperimentData):
    print(f"Processing experiment {exp.name}")
    create_plots_for_experiment(exp, data)


def process_experiment_batch_output(batch: list[Experiment]):
    for exp in batch:
        exp_data: JoinedExperimentData = experiment_data_from_all_series(exp)
        process_experiment_data(exp, exp_data)


