from solver import SolverProxy, SolverParams, SolverRunMetadata
from .config import ExperimentBatchDesc
from .model import ExperimentResult, ExperimentDesc
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


def base_output_path_resolver(input_file: Path, output_dir: Path, series_id: Optional[int] = None) -> Path:
    file_name = input_file.stem + \
        '-result' + \
        ('-run-' + str(series_id)) if series_id is not None else ''
    return output_dir.joinpath(file_name).with_suffix('.txt')


class ExperimentBatchRunner:
    def __init__(self, solver: SolverProxy, batch_desc: ExperimentBatchDesc):
        self.solver: SolverProxy = solver
        self.batch_desc: ExperimentBatchDesc = batch_desc
        self.runner: ExperimentRunner = ExperimentRunner(self.solver)

    def run(self) -> list[ExperimentResult]:
        return [self.runner.run(desc) for desc in self.batch_desc.descriptions]


class ExperimentRunner:
    def __init__(self, solver: SolverProxy):
        self.solver: SolverProxy = solver

    def run(self, desc: ExperimentDesc) -> ExperimentResult:
        run_metadata: list[SolverRunMetadata] = []
        output_files: list[Path] = []
        for sid in range(1, desc.repeats_no + 1):
            out_file = base_output_path_resolver(desc.input_file, desc.output_dir, sid)
            params = SolverParams(desc.input_file, out_file)
            metadata = self.solver.run(params)
            output_files.append(out_file)
            run_metadata.append(metadata)
        return ExperimentResult(desc, run_metadata, output_files)

