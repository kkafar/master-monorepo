from typing import Dict
from experiment.model import (
    SeriesOutputMetadata,
    Experiment,
    InstanceMetadata,
    ExperimentConfig
)


def deserialize_series_metadata_from_dict(metadata_dict: Dict) -> SeriesOutputMetadata:
    return SeriesOutputMetadata(
        solution_string=metadata_dict["solution_string"],
        hash=metadata_dict["hash"],
        fitness=metadata_dict["fitness"],
        generation_count=metadata_dict["generation_count"],
        total_time=metadata_dict["total_time"],
        chromosome=metadata_dict["chromosome"]
    )


def deserialize_experiment_from_dict(exp_dict: dict):
    # Some hacks here as Python does not use any kin o type annotation
    # so it does not know how to serialize nested objects... what a language!
    if exp_dict.get("id") is not None:
        return InstanceMetadata.from_dict(exp_dict)
    elif exp_dict.get("input_file") is not None:
        return ExperimentConfig.from_dict(exp_dict)
    else:
        return Experiment.from_dict(exp_dict)

