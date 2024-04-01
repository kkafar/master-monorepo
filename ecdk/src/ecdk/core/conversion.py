from experiment.model import (
    Experiment,
    InstanceMetadata,
    ExperimentConfig
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

