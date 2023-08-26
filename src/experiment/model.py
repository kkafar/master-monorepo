from dataclasses import dataclass
from pathlib import Path
from solver import SolverResult


@dataclass
class ExperimentDescription:
    name: str
    input_file: Path
    output_dir: Path
    repeats_no: int


@dataclass
class ExperimentResult:
    description: ExperimentDescription
    run_results: list[SolverResult]
    output_files: list[Path]
