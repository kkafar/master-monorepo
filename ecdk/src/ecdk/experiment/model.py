from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, TypeAlias
from data.model import InstanceMetadata
from core.version import Version
import core.util
from polars import DataFrame
import datetime as dt
import json

ExperimentId: TypeAlias = str
ExperimentFamily: TypeAlias = str
SolutionHash: TypeAlias = str
SolutionStr: TypeAlias = str


@dataclass(frozen=True)
class SolverExecutableInfo:
    """ Information on solver binary that was used for particular batch """

    version: Version = field(default=Version(0, 1, 0))

    @classmethod
    def from_dict(cls, md: dict):
        return cls(
            version=Version.from_str(md['version'])
        )

    def as_dict(self) -> dict:
        return {
            "version": str(self.version),
        }


@dataclass(frozen=True)
class EcdkInfo:
    """ Information on ecdk application used to conduct experiments / analyze data etc. """
    version: Version = field(default=Version(0, 0, 1))

    @classmethod
    def from_dict(cls, md: dict):
        return cls(
            version=Version.from_str(md.get('version', '0.0.1'))
        )

    def as_dict(self) -> dict:
        return {
            "version": str(self.version),
        }


@dataclass(frozen=True)
class SeriesOutputFiles:
    """ Describes structure of output directory for given **series** of given experiment """

    # Path to the series output directory
    directory: Path

    # Mapping of csv event files (see docs on model for format explanation). EventName -> Path
    event_files: Dict[str, Path]

    # Path to the summary of solver output. This file is in JSON format & contains
    # information defined by the `SeriesOutputMetadata` type
    run_metadata_file: Path

    # Stdout file of solver process for given series. Logs, errors, warnings of the solver
    logfile: Optional[Path]


@dataclass(frozen=True)
class SeriesOutputMetadata:
    """ Solver produces file (right now named `run_metadata.json`) with summary information about
    results of single run (single series). This structure models content of this file """

    solution_string: str
    hash: str
    fitness: int
    generation_count: int
    total_time: int
    chromosome: list[float]

    # These are optional because they were just recently introduced
    # and older computation results do not have them!
    age_avg: Optional[float]
    age_max: Optional[int]
    individual_count: Optional[int]
    crossover_involvement_max: Optional[int]
    crossover_involvement_min: Optional[int]
    start_timestamp: Optional[str]
    end_timestamp: Optional[str]

    @classmethod
    def from_dict(cls, md: Dict):
        return cls(
            solution_string=md["solution_string"],
            hash=md["hash"],
            fitness=md["fitness"],
            generation_count=md["generation_count"],
            total_time=md["total_time"],
            chromosome=md["chromosome"],
            age_avg=md.get("age_avg"),
            age_max=md.get("age_max"),
            individual_count=md.get("individual_count"),
            crossover_involvement_max=md.get("crossover_involvement_max"),
            crossover_involvement_min=md.get("crossover_involvement_min"),
            start_timestamp=md.get("start_timestamp"),
            end_timestamp=md.get("end_timestamp"),
        )


@dataclass(frozen=True)
class SeriesOutputData:
    """ In-memory representation of solver output for single run (series output). Holds event information
    in polars DataFrames & additional "metadata" (no idea why I've named it this way) with direct solver result.
    """

    # Mapping EventName -> DataFrame. Each event has a bit different schema. See docs for reference.
    event_data: Dict[str, DataFrame]
    metadata: SeriesOutputMetadata

    def data_for_event(self, event: str) -> Optional[DataFrame]:
        return self.event_data.get(event, None)


@dataclass
class SeriesOutput:
    """ A bit weird type, that holds both the reference (paths of files with single series output data) and if materialized
    (see `is_materialized` method), also holds the data loaded to memory. """

    data: Optional[SeriesOutputData]
    files: SeriesOutputFiles

    def is_materialized(self) -> bool:
        return self.data is not None


@dataclass
class SolverParams:
    """ Models CLI parameters of solver binary. These together with `SolverProxy` instance can be turned into solver invocation.
    TODO: This could be placed somewhere near the solver. I should move away from placing types definition in typescript .d files fashion."""
    input_file: Optional[Path]
    output_dir: Optional[Path]
    config_file: Optional[Path]
    stdout_file: Optional[Path]


@dataclass
class SolverRunMetadata:
    """ Data collected by the runtime process (scheduler) on single solver proces (used for solving single series).
    This is used only in by the "Local" solver, that keeps the runtime process alive for the time of scheduling - this is not used
    in case of HyperQueue.
    """

    duration: dt.timedelta
    status: int  # Executing process return code

    def is_ok(self) -> bool:
        """ Whether the computation completed without any errors """
        return self.status == 0


@dataclass
class SolverResult:
    """ Aggregate type holding both: actual solver single series output and some metadata collected by the scheduler.
    Similarly to `SolverRunMetadata` this is used only in case of "local" solver (for the same reasons).
    """
    series_output: SeriesOutput
    run_metadata: SolverRunMetadata


@dataclass
class SolverConfigFileContents:
    """ Models config file that can be passed to the solver. We load this file to acquire some additional metadata for experiment batch description
    such as solver type. Most of the values might be not present as solver provides defaults. """

    # Path to file with instance specification. Usually not present as it is series dependend. See comment on `output_dir`.
    input_file: Optional[Path]

    # Path to directory where solver output will be put. This currently corresponds to single series output directory.
    # In usual setup I do not specify this in config file passed to a solver, as it would be problematic to have
    # separate config file for each series.
    output_dir: Optional[Path]

    # Number of generations to run the solver for.
    n_gen: Optional[int]

    # Size of population.
    pop_size: Optional[int]

    # Constant factor used during fitness evaluation. See solver source code for description.
    delay_const_factor: Optional[float]

    # Solver type to run. If not present `default` is being used.
    solver_type: Optional[str]

    # Not adding rest of the fields for now, as most of them is unset
    # in solver config file anyway...

    @classmethod
    def from_dict(cls, d: Dict):
        return SolverConfigFileContents(
            input_file=core.util.nonesafe_map(d.get("input_file"), Path),
            output_dir=core.util.nonesafe_map(d.get("output_dir"), Path),
            n_gen=core.util.nonesafe_map(d.get("n_gen"), int),
            pop_size=core.util.nonesafe_map(d.get("pop_size"), int),
            delay_const_factor=core.util.nonesafe_map(d.get("delay_const_factor"), float),
            solver_type=d.get("solver_type") or "default"
        )

    def as_dict(self):
        return {
            "input_file": self.input_file,
            "output_dir": self.output_dir,
            "n_gen": self.n_gen,
            "pop_size": self.pop_size,
            "delay_const_factor": self.delay_const_factor,
            "solver_type": self.solver_type
        }


class SolverConfigFile:
    def __init__(self, path: Path):
        self.path = path
        self._contents: SolverConfigFileContents = None

    @property
    def contents(self) -> SolverConfigFileContents:
        if self._contents is None:
            with open(self.path, 'r') as file:
                self._contents = json.load(file, object_hook=SolverConfigFileContents.from_dict)
        return self._contents


@dataclass(frozen=True)
class ExperimentConfig:
    """ Experiment is a series of solver runs over single test case. """

    # Path to file with JSSP instance specification
    input_file: Path

    # Path to directory, where subdirectories for given series outputs will be created
    output_dir: Path

    # Optional path to solver config file, this should be passed throught directly to solver
    config_file: Optional[Path]

    # Number of repetitions to run for this experiment
    n_series: int

    def as_dict(self) -> dict:
        return {
            "input_file": str(self.input_file),
            "output_dir": str(self.output_dir),
            "n_series": self.n_series,
            "config_file": str(self.config_file),
        }

    @classmethod
    def from_dict(cls, d: dict) -> 'ExperimentConfig':
        return ExperimentConfig(
            input_file=Path(d['input_file']),
            output_dir=Path(d['output_dir']),
            config_file=Path(d.get('config_file')),
            n_series=int(d['n_series']),
        )


@dataclass
class ExperimentResult:
    """ Results of all the series of given experiment & optional associated metadata collected by the scheduler.
    Metadata is present only in case of "local" solver (for the same reasons as for many of the types above). """

    """ Each experiment series output is stored in separate directory """
    series_outputs: list[SeriesOutput]

    """ Computations might be repeated > 1 times to average results,
        hence `run_metadata` is a list """
    metadata: Optional[list[SolverRunMetadata]] = None

    def n_series(self) -> int:
        return len(self.series_outputs)

    def has_metadata(self) -> bool:
        return self.metadata is not None


@dataclass
class Experiment:
    """ Instance description, run configuration, result obtained """
    name: ExperimentId
    instance: InstanceMetadata
    config: ExperimentConfig  # TODO: Flatten the structure and pass whole Experiment around
    result: Optional[ExperimentResult] = None

    # Directory of the batch this experiment belongs to. Usually the file hierarchy would be
    # batch_dir/config.output_dir.
    batch_dir: Optional[Path] = None  # TODO: Make this not optional

    def has_result(self) -> bool:
        return self.result is not None

    def as_dict(self) -> dict:
        # result field is not serialized on purpose
        # it enforces thoughts that result should not be stored in this class
        return {
            "name": self.name,
            "instance": self.instance.as_dict(),
            "config": self.config.as_dict(),
        }

    @classmethod
    def from_dict(cls, exp_dict: dict) -> 'Experiment':
        # Some hacks here as Python does not use any kin o type annotation
        # so it does not know how to serialize nested objects... what a language!
        if exp_dict.get("id") is not None:
            return InstanceMetadata.from_dict(exp_dict)
        elif exp_dict.get("input_file") is not None:
            return ExperimentConfig.from_dict(exp_dict)
        else:
            return cls(name=exp_dict["name"],
                       instance=exp_dict["instance"],
                       config=exp_dict["config"])


@dataclass
class ExperimentBatch:
    """  """

    # Output directory of whole experiment batch (list of experiments)
    output_dir: Path

    # List of experiments to conduct
    experiments: list[Experiment]

    solver_config: Optional[SolverConfigFile]

    # ISO 8601 timestamp
    start_time: Optional[str] = None

    solver_info: Optional[SolverExecutableInfo] = None
    ecdk_info: Optional[EcdkInfo] = None

    def as_dict(self) -> dict:
        result = {
            "output_dir": str(self.output_dir),
            "configs": list(map(lambda e: e.as_dict(), self.experiments))  # This field is named configs for compatibility reasons
        }

        if self.solver_config is not None:
            result["solver_config"] = self.solver_config.contents.as_dict()

        if self.start_time:
            result["start_time"] = self.start_time

        if self.solver_info is not None:
            result["solver_info"] = self.solver_info.as_dict()

        if self.ecdk_info is not None:
            result["ecdk_info"] = self.ecdk_info.as_dict()

        return result


@dataclass
class SolverRunConfig:
    """This mirrors sturct internally used by solver, which is output to solver's
    stdout and we're trying to parse it here. This shouldn't be used in any
    any different place."""

    pop_size: int
    n_gen: int
    elitism_rate: float
    sampling_rate: float
    delay_const_factor: float
    local_search_enabled: bool

    @classmethod
    def from_dict(cls, md: dict):
        return cls(
            pop_size=md['pop_size'],
            n_gen=md['n_gen'],
            elitism_rate=md['elitism_rate'],
            sampling_rate=md['sampling_rate'],
            delay_const_factor=md['delay_const_factor'],

            # When not set it defaults to True. Also allows for backward compat.
            local_search_enabled=md.get('local_search_enabled', True),
        )


@dataclass
class SolverDescription:
    """ Solver outputs this to stdout every time it is run. """

    codename: str
    run_cfg: SolverRunConfig
    description: str
    version: Version

    @classmethod
    def from_dict(cls, md: dict):
        if "pop_size" in md.keys():
            return SolverRunConfig.from_dict(md)

        return cls(
            codename=md['codename'],
            run_cfg=md['run_cfg'],
            description=md['description'],

            # 0.1.0 was the version before introducing this field to solver description
            version=Version.from_str(md.get("version", "0.1.0")),
        )

