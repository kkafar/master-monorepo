from dataclasses import dataclass
from pathlib import Path


@dataclass
class SolverInput:
    input_file: Path
    output_file: Path


