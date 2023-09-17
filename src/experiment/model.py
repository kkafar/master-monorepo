from dataclasses import dataclass
from pathlib import Path
from .solver import SolverRunMetadata
from typing import Optional
from data.model import InstanceMetadata


@dataclass(frozen=True)
class ExperimentConfig:
    """ Experiment is a series of solver runs over single test case """
    name: str
    input_file: Path
    output_dir: Path
    repeats_no: int


@dataclass
class ExperimentResult:
    config: ExperimentConfig

    """ Each experiment series output is stored in separate file """
    output_files: list[Path]

    """ Computations might be repeated > 1 times to average results,
        hence `run_metadata` is a list """
    run_metadata: Optional[list[SolverRunMetadata]] = None

    """ Optional information on lower bound, best known
        solution, etc. """
    instance_metadata: Optional[InstanceMetadata] = None


@dataclass
class ExperimentBundle:
    """ Instance description, run configuration, result obtained """
    instance: InstanceMetadata
    run_config: ExperimentConfig
    run_result: Optional[ExperimentResult] = None

    def has_result(self) -> bool:
        return self.run_result is not None
