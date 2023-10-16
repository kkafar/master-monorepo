from typing import Dict
from experiment.model import SeriesOutputMetadata, Experiment


def deserialize_series_metadata_from_dict(metadata_dict: Dict) -> SeriesOutputMetadata:
    return SeriesOutputMetadata(
        solution_string=metadata_dict["solution_string"],
        hash=metadata_dict["hash"],
        fitness=metadata_dict["fitness"],
        generation_count=metadata_dict["generation_count"],
        total_time=metadata_dict["total_time"],
        chromosome=metadata_dict["chromosome"]
    )


def deserialize_experiment_from_dict(exp_dict: dict) -> Experiment:
    return Experiment.from_dict(exp_dict)


