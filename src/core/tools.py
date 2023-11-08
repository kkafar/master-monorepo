import datetime as dt
from typing import Dict
from pathlib import Path
from data.model import (
    InstanceMetadata,
)
from experiment.model import (
    Experiment,
    ExperimentResult
)


def create_experiments_form_results(
        results: list[ExperimentResult],
        metadata_store: Dict[str, InstanceMetadata]) -> list[Experiment]:
    return [
        Experiment(
            metadata_store.get(result.name),
            result.config,
            result
        )
        for result in results
    ]


def exp_name_from_input_file(input_file: Path) -> str:
    return input_file.stem


def base_output_path_resolver(input_file: Path, output_dir: Path) -> Path:
    return output_dir.joinpath(input_file.stem + '-result').with_suffix('.txt')


def output_dir_for_experiment_with_name(name: str, base_dir: Path) -> Path:
    return base_dir.joinpath(name)


def current_timestamp() -> str:
    timestamp = dt.datetime.now().strftime("%y-%m-%dT%H-%M-%S")
    return timestamp


def attach_timestamp_to_dir(directory: Path, timestamp: str) -> Path:
    return directory.joinpath(timestamp)
