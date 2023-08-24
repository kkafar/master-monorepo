from solver import SolverProxy, SolverParams, SolverResult
from .config import RunInfo
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


def base_output_path_resolver(input_file: Path, output_dir: Path, series_id: Optional[int] = None) -> Path:
    file_name = input_file.stem + \
        '-result' + \
        ('-run-' + str(series_id)) if series_id is not None else ''
    return output_dir.joinpath(file_name).with_suffix('.txt')


@dataclass
class ExperimentResult:
    name: str
    params: SolverParams
    run_results: list[SolverResult]


class Runner:
    solver: SolverProxy
    config: RunInfo

    def __init__(self, solver: SolverProxy, config: RunInfo):
        self.solver = solver
        self.config = config

    def run(self) -> list[ExperimentResult]:
        results: list[ExperimentResult] = []
        for exp_data in self.config.descriptions:
            name = self.exp_name_from_input_file(exp_data.input_file)
            run_results = []
            for series_id in range(1, exp_data.repeats_no + 1):
                output_file = base_output_path_resolver(exp_data.input_file, exp_data.output_dir, series_id)
                params = SolverParams(exp_data.input_file, output_file)
                run_result = self.solver.run(params)
                run_results.append(run_results)
            results.append(ExperimentResult(name, params, [run_result]))
        return results

    def exp_name_from_input_file(self, input_file: Path) -> str:
        return input_file.stem

