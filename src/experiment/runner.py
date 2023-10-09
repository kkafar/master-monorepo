from .solver import SolverProxy, SolverParams, SolverRunMetadata
from .model import ExperimentResult, ExperimentConfig
from pathlib import Path
from typing import Optional


def base_output_dir_resolver(input_file: Path, output_dir: Path, series_id: Optional[int] = None) -> Path:
    file_name = input_file.stem + \
        '-result' + \
        ('-run-' + str(series_id)) if series_id is not None else ''
    return output_dir.joinpath(file_name).with_suffix('.txt')


def simple_output_dir_resolver(base_output_dir: Path, series_id: int) -> Path:
    dir_name = base_output_dir.stem + \
        '-series-' + \
        str(series_id)
    return base_output_dir.joinpath(dir_name)


class ExperimentBatchRunner:
    def __init__(self, solver: SolverProxy, configs: list[ExperimentConfig]):
        self.solver: SolverProxy = solver
        self.configs: list[ExperimentConfig] = configs
        self.runner: ExperimentRunner = ExperimentRunner(self.solver)

    def run(self, process_limit: int = 1) -> list[ExperimentResult]:
        assert process_limit >= 1, "Process limit must be >= 0"
        if process_limit == 1:
            return [self.runner.run(desc) for desc in self.configs]
        else:
            return self.runner.run_in_parallel(self.configs, process_limit)


class ExperimentRunner:
    def __init__(self, solver: SolverProxy):
        self.solver: SolverProxy = solver

    def run(self, config: ExperimentConfig) -> ExperimentResult:
        run_metadata: list[SolverRunMetadata] = []
        output_dirs: list[Path] = []
        for sid in range(0, config.n_series):
            out_dir = simple_output_dir_resolver(config.output_dir, sid)
            params = SolverParams(config.input_file, out_dir)
            metadata = self.solver.run(params)
            output_dirs.append(out_dir)
            run_metadata.append(metadata)
        return ExperimentResult(output_dirs, run_metadata)

    def run_in_parallel(self, configs: list[ExperimentConfig], process_limit: int = 1) -> list[ExperimentResult]:
        params = []
        results = []
        for cfg in configs:
            result = ExperimentResult(output_dirs=[], run_metadata=[])
            for sid in range(0, cfg.n_series):
                out_dir = simple_output_dir_resolver(cfg.output_dir, sid)
                result.output_dirs.append(out_dir)
                params.append(SolverParams(cfg.input_file, out_dir))
            results.append(result)

        mds = self.solver.run_nonblocking(params, process_limit)
        for res, md in zip(results, mds):
            res.run_metadata = md
        return results

