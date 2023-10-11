from .solver import SolverProxy, SolverParams, SolverRunMetadata, SolverResult
from .model import ExperimentResult, ExperimentConfig, SeriesOutput
from pathlib import Path
from typing import Optional
from core.util import iter_batched


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
        series_outputs: list[SeriesOutput] = []
        for sid in range(0, config.n_series):
            out_dir = simple_output_dir_resolver(config.output_dir, sid)
            params = SolverParams(config.input_file, out_dir)
            solver_result: SolverResult = self.solver.run(params)
            series_outputs.append(solver_result.series_output)
            run_metadata.append(solver_result.run_metadata)
        return ExperimentResult(series_outputs=series_outputs, run_metadata=run_metadata)

    def run_in_parallel(self, configs: list[ExperimentConfig], process_limit: int = 1) -> list[ExperimentResult]:
        params = []
        for cfg in configs:
            for sid in range(0, cfg.n_series):
                out_dir = simple_output_dir_resolver(cfg.output_dir, sid)
                params.append(SolverParams(cfg.input_file, out_dir))

        solver_results = self.solver.run_nonblocking(params, process_limit)

        # lets assert that chunks are equal
        n_series = configs[0].n_series
        assert all(map(lambda cfg: cfg.n_series == n_series, configs))
        assert len(solver_results) % n_series == 0

        results: list[ExperimentResult] = []
        for solver_result_batch in iter_batched(solver_results, n_series):
            results.append(ExperimentResult(
                series_outputs=list(map(lambda res: res.series_output, solver_result_batch)),
                run_metadata=list(map(lambda res: res.run_metadata, solver_result_batch))
            ))
        return results

