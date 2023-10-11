from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict
from data.model import InstanceMetadata
from polars import DataFrame
import datetime as dt


@dataclass(frozen=True)
class SeriesOutputFiles:
    directory: Path
    event_files: Dict[str, Path]
    run_metadata_file: Path


@dataclass(frozen=True)
class SeriesOutputMetadata:
    solution_string: str
    hash: str
    fitness: int
    generation_count: int
    total_time: int


@dataclass(frozen=True)
class SeriesOutputData:
    event_data: Dict[str, DataFrame]
    metadata: SeriesOutputMetadata

    def data_for_event(self, event: str) -> Optional[DataFrame]:
        return self.event_data.get(event, None)


@dataclass
class SeriesOutput:
    data: Optional[SeriesOutputData]
    files: SeriesOutputFiles

    def is_materialized(self) -> bool:
        return self.data is None


@dataclass
class SolverParams:
    input_file: Path
    output_dir: Path


@dataclass
class SolverRunMetadata:
    duration: dt.timedelta


@dataclass
class SolverResult:
    series_output: SeriesOutput
    run_metadata: SolverRunMetadata


@dataclass(frozen=True)
class ExperimentConfig:
    """ Experiment is a series of solver runs over single test case """
    input_file: Path
    output_dir: Path
    n_series: int


@dataclass
class ExperimentResult:

    """ Each experiment series output is stored in separate directory """
    series_outputs: list[SeriesOutput]

    """ Computations might be repeated > 1 times to average results,
        hence `run_metadata` is a list """
    run_metadata: Optional[list[SolverRunMetadata]] = None


@dataclass
class Experiment:
    """ Instance description, run configuration, result obtained """
    name: str
    instance: InstanceMetadata
    run_config: ExperimentConfig
    run_result: Optional[ExperimentResult] = None

    def has_result(self) -> bool:
        return self.run_result is not None

