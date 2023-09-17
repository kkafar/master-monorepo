from .solver import SolverProxy, SolverParams, SolverRunMetadata
from .config import ExperimentBatchConfig
from .model import ExperimentResult, ExperimentConfig
from pathlib import Path
from typing import Optional


def base_output_path_resolver(input_file: Path, output_dir: Path, series_id: Optional[int] = None) -> Path:
    file_name = input_file.stem + \
        '-result' + \
        ('-run-' + str(series_id)) if series_id is not None else ''
    return output_dir.joinpath(file_name).with_suffix('.txt')


class ExperimentBatchRunner:
    def __init__(self, solver: SolverProxy, batch_config: ExperimentBatchConfig):
        self.solver: SolverProxy = solver
        self.batch_config: ExperimentBatchConfig = batch_config
        self.runner: ExperimentRunner = ExperimentRunner(self.solver)

    def run(self) -> list[ExperimentResult]:
        return [self.runner.run(desc) for desc in self.batch_config.configs]


class ExperimentRunner:
    def __init__(self, solver: SolverProxy):
        self.solver: SolverProxy = solver

    def run(self, config: ExperimentConfig) -> ExperimentResult:
        run_metadata: list[SolverRunMetadata] = []
        output_files: list[Path] = []
        for sid in range(1, config.repeats_no + 1):
            out_file = base_output_path_resolver(config.input_file, config.output_dir, sid)
            params = SolverParams(config.input_file, out_file)
            metadata = self.solver.run(params)
            output_files.append(out_file)
            run_metadata.append(metadata)
        return ExperimentResult(config, output_files, run_metadata)

