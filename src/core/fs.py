import json
from pathlib import Path
from experiment.model import Experiment


def experiment_file_resolver(experiment: Experiment) -> Path:
    return experiment.config.output_dir.joinpath('experiment').with_suffix('.json')


def simple_output_dir_resolver(base_output_dir: Path, series_id: int) -> Path:
    dir_name = base_output_dir.stem + \
        '-series-' + \
        str(series_id)
    return base_output_dir.joinpath(dir_name)


# def dump_run_metadata()


def initialize_file_hierarchy(experiments: list[Experiment]):
    """ Creates directory structure for the output & dumps experiments / series configuration
    to appriopriate directories """
    for experiment in experiments:
        experiment.config.output_dir.mkdir(parents=True, exist_ok=True)
        for series_i in range(0, experiment.config.n_series):
            series_dir = simple_output_dir_resolver(experiment.config.output_dir, series_i)
            series_dir.mkdir(parents=True, exist_ok=True)

        experiment_file = experiment_file_resolver(experiment)
        with open(experiment_file, 'w') as file:
            json.dump(experiment.as_dict(), file)


