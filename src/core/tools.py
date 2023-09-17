from typing import Dict
from data.model import (
    InstanceMetadata,
)
from experiment.model import (
    ExperimentBundle,
    ExperimentConfig,
    ExperimentResult
)


def create_exp_bundles_from_results(
        results: list[ExperimentResult],
        metadata_store: Dict[str, InstanceMetadata]) -> list[ExperimentBundle]:
    return [
        ExperimentBundle(
            metadata_store.get(result.name),
            result.config,
            result
        )
        for result in results
    ]
        
