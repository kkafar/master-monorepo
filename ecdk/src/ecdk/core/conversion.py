from typing import Dict
from experiment.model import (
    SeriesOutputMetadata,
    Experiment,
    InstanceMetadata,
    ExperimentConfig
)


def deserialize_series_metadata_from_dict(md: Dict) -> SeriesOutputMetadata:
    return SeriesOutputMetadata(
        solution_string=md["solution_string"],
        hash=md["hash"],
        fitness=md["fitness"],
        generation_count=md["generation_count"],
        total_time=md["total_time"],
        chromosome=md["chromosome"],
        age_avg=md.get("age_avg"),
        individual_count=md.get("individual_count"),
        crossover_involvement_max=md.get("crossover_involvement_max"),
        crossover_involvement_min=md.get("crossover_involvement_min")
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

