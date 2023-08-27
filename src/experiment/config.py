from pathlib import Path
from typing import Optional, Callable
from .model import ExperimentDescription


def base_output_path_resolver(input_file: Path, output_dir: Path) -> Path:
    return output_dir.joinpath(input_file.stem + '-result').with_suffix('.txt')


def exp_name_from_input_file(input_file: Path) -> str:
    return input_file.stem


class ExperimentBatchDesc:
    descriptions: list[ExperimentDescription]
    output_path_resolver: Callable[[Path, Path], Path]

    def __init__(self,
                 inputs: list[Path],
                 output_file: Optional[Path] = None,
                 output_dir: Optional[Path] = None,
                 repeats_no: int = 1,
                 output_path_resolver: Callable[[Path, Path], Path] = base_output_path_resolver):
        self.output_path_resolver = output_path_resolver

        if output_dir is None:
            output_dir = ExperimentBatchDesc.default_output_dir()

        if len(inputs) == 1:
            input_file = inputs[0]
            if output_file is None:
                output_file = self.output_path_resolver(input_file, output_dir)
            self.descriptions = [ExperimentDescription(name=exp_name_from_input_file(input_file),
                                                       input_file=input_file,
                                                       output_dir=output_dir,
                                                       repeats_no=repeats_no)]
            return

        self.descriptions = [
            ExperimentDescription(name=exp_name_from_input_file(input_file), input_file=input_file,
                                  output_dir=output_dir, repeats_no=repeats_no)
            for input_file in inputs
        ]

    @classmethod
    def default_output_file(cls) -> Path:
        return Path("result.txt")

    @classmethod
    def default_output_dir(cls) -> Path:
        return Path("output")

