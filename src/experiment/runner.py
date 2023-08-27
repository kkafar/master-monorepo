from solver import SolverProxy, SolverParams
from .config import ExperimentBatchDesc
from .model import ExperimentResult
from pathlib import Path
from typing import Optional


def base_output_path_resolver(input_file: Path, output_dir: Path, series_id: Optional[int] = None) -> Path:
    file_name = input_file.stem + \
        '-result' + \
        ('-run-' + str(series_id)) if series_id is not None else ''
    return output_dir.joinpath(file_name).with_suffix('.txt')


class Runner:
    solver: SolverProxy
    config: ExperimentBatchDesc

    def __init__(self, solver: SolverProxy, config: ExperimentBatchDesc):
        self.solver = solver
        self.config = config

    def run(self) -> list[ExperimentResult]:
        results: list[ExperimentResult] = []
        for desc in self.config.descriptions:
            run_metadata = []
            output_files = []
            for series_id in range(1, desc.repeats_no + 1):
                output_file = base_output_path_resolver(
                    desc.input_file, desc.output_dir, series_id)
                params = SolverParams(desc.input_file, output_file)
                solver_result = self.solver.run(params)
                output_files.append(output_file)
                run_metadata.append(solver_result)
            results.append(ExperimentResult(desc, run_metadata, output_files))
        return results

