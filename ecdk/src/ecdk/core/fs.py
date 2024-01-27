import json
from pathlib import Path
from experiment.model import Experiment


def experiment_file_from_directory(directory: Path) -> Path:
    return directory.joinpath('experiment').with_suffix('.json')


def experiment_file_resolver(experiment: Experiment) -> Path:
    return experiment_file_from_directory(experiment.config.output_dir)


def output_dir_for_series(base_output_dir: Path, series_id: int) -> Path:
    dir_name = base_output_dir.stem + \
        '-series-' + \
        str(series_id)
    return base_output_dir.joinpath(dir_name)


def solver_logfile_for_series(base_output_dir: Path, series_id: int) -> Path:
    directory = output_dir_for_series(base_output_dir, series_id)
    return directory.joinpath('stdout.log')


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
            series_dir = output_dir_for_series(experiment.config.output_dir, series_i)
            series_dir.mkdir(parents=True, exist_ok=True)

        experiment_file = experiment_file_resolver(experiment)
        with open(experiment_file, 'w') as file:
            json.dump(experiment.as_dict(), file, indent=4)


def get_main_plotdir(basedir: Path) -> Path:
    return basedir.joinpath('plots')


def get_plotdir_for_exp(exp: Experiment, basedir: Path) -> Path:
    return get_main_plotdir(basedir).joinpath(exp.name)


def get_main_tabledir(basedir: Path) -> Path:
    return basedir.joinpath('tables')


def get_tabledir_for_exp(exp: Experiment, basedir: Path) -> Path:
    return get_main_tabledir(basedir).joinpath(exp.name)


def init_processed_data_file_hierarchy(exps: list[Experiment], basedir: Path):
    get_main_plotdir(basedir).mkdir(parents=True, exist_ok=True)
    get_main_tabledir(basedir).mkdir(parents=True, exist_ok=True)

    for exp in exps:
        get_plotdir_for_exp(exp, basedir).mkdir(parents=True, exist_ok=True)

        # We do not need tabledir per experiment right now
        # Uncomment it once there is some per-experiment anaylisis done
        # get_tabledir_for_exp(exp, basedir).mkdir(parents=True, exist_ok=True)









