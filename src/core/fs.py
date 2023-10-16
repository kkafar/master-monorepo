import json
from pathlib import Path
from experiment.model import Experiment


def experiment_file_from_directory(directory: Path) -> Path:
    return directory.joinpath('experiment').with_suffix('.json')


def experiment_file_resolver(experiment: Experiment) -> Path:
    return experiment_file_from_directory(experiment.config.output_dir)


def simple_output_dir_resolver(base_output_dir: Path, series_id: int) -> Path:
    dir_name = base_output_dir.stem + \
        '-series-' + \
        str(series_id)
    return base_output_dir.joinpath(dir_name)


# TODO: This function should not be here
def dump_exp_batch_config(config_file: Path, experiments: list[Experiment]):
    joined_config = {
        "configs": list(map(lambda e: e.as_dict(), experiments))
    }

    with open(config_file, 'w') as file:
        json.dump(joined_config, file, indent=4)


# TODO: This function should not be here
def initialize_file_hierarchy(experiments: list[Experiment]):
    """ Creates directory structure for the output & dumps experiments / series configuration

    to appriopriate directories """

    assert len(experiments) > 0, "No experiments were specified"

    base_dir = experiments[0].config.output_dir.parent
    base_dir.mkdir(parents=True, exist_ok=True)
    config_file = base_dir.joinpath("config.json")

    dump_exp_batch_config(config_file, experiments)

    for experiment in experiments:
        experiment.config.output_dir.mkdir(parents=True, exist_ok=True)
        for series_i in range(0, experiment.config.n_series):
            series_dir = simple_output_dir_resolver(experiment.config.output_dir, series_i)
            series_dir.mkdir(parents=True, exist_ok=True)

        experiment_file = experiment_file_resolver(experiment)
        with open(experiment_file, 'w') as file:
            json.dump(experiment.as_dict(), file, indent=4)


