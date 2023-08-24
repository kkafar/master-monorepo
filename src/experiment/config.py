from pathlib import Path
from typing import Optional, Callable
from solver import SolverParams


def default_output_path_resolver(input_file: Path, output_dir: Path) -> Path:
    return output_dir.joinpath(input_file.stem + '-result').with_suffix('.txt')


class ExpConfig:
    configurations: list[SolverParams]
    output_path_resolver: Callable[[Path, Path], Path]

    def __init__(self,
                 inputs: list[Path],
                 output_file: Optional[Path] = None,
                 output_dir: Optional[Path] = None,
                 output_path_resolver: Callable[[Path, Path], Path] = default_output_path_resolver):
        self.output_path_resolver = output_path_resolver

        if output_dir is None:
            output_dir = ExpConfig.default_output_dir()

        if len(inputs) == 1:
            if output_file is None:
                output_file = self.output_path_resolver(inputs[0], output_dir)
            self.configurations = [SolverParams(input_file=inputs[0],
                                               output_file=output_file)]
            return

        self.configurations = [
            SolverParams(input_file=input_file,
                         output_file=self.output_path_resolver(input_file, output_dir))
            for input_file in inputs
        ]

    @classmethod
    def default_output_file(cls) -> Path:
        return Path("result.txt")

    @classmethod
    def default_output_dir(cls) -> Path:
        return Path("output")

