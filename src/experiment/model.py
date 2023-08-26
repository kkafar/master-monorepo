from dataclasses import dataclass
from pathlib import Path
from solver import SolverResult


@dataclass(frozen=True)
class ExperimentDescription:
    """ Experiment is a series of solver runs over single test case """
    name: str
    input_file: Path
    output_dir: Path
    repeats_no: int


@dataclass
class ExperimentResult:
    description: ExperimentDescription

    """ Computations might be repeated > 1 times to average results,
        hence `run_results` is a list """
    run_results: list[SolverResult]

    """ Each experiment series output is stored in separate file """
    output_files: list[Path]
