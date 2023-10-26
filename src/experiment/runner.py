from .solver import SolverProxy, SolverParams, SolverRunMetadata, SolverResult
from .model import ExperimentResult, ExperimentConfig, SeriesOutput
from core.util import iter_batched
from core.fs import simple_output_dir_resolver
from core.env import ArrayJobSpec, input_range_from_jobspec


class LocalExperimentBatchRunner:
    def __init__(self, solver: SolverProxy, configs: list[ExperimentConfig]):
        self.solver: SolverProxy = solver
        self.configs: list[ExperimentConfig] = configs
        self.runner: LocalExperimentRunner = LocalExperimentRunner(self.solver)

    def run(self, process_limit: int = 1) -> list[ExperimentResult]:
        assert process_limit >= 1, "Process limit must be >= 0"
        if process_limit == 1:
            return [self.runner.run(desc) for desc in self.configs]
        else:
            return self.runner.run_in_parallel(self.configs, process_limit)


class LocalExperimentRunner:
    def __init__(self, solver: SolverProxy):
        self.solver: SolverProxy = solver

    def _params_from_configs(self, configs: list[ExperimentConfig]) -> list[SolverParams]:
        params = []
        for cfg in configs:
            for sid in range(0, cfg.n_series):
                out_dir = simple_output_dir_resolver(cfg.output_dir, sid)
                params.append(SolverParams(cfg.input_file, out_dir))
        return params

    def run(self, config: ExperimentConfig) -> ExperimentResult:
        run_metadata: list[SolverRunMetadata] = []
        series_outputs: list[SeriesOutput] = []
        for sid in range(0, config.n_series):
            out_dir = simple_output_dir_resolver(config.output_dir, sid)
            params = SolverParams(config.input_file, out_dir)
            solver_result: SolverResult = self.solver.run(params)
            series_outputs.append(solver_result.series_output)
            run_metadata.append(solver_result.run_metadata)
        return ExperimentResult(series_outputs=series_outputs, metadata=run_metadata)

    def run_in_parallel(self, configs: list[ExperimentConfig], process_limit: int = 1) -> list[ExperimentResult]:
        params = self._params_from_configs(configs)

        solver_results = self.solver.run_nonblocking(params, process_limit)

        # lets assert that chunks are equal
        n_series = configs[0].n_series
        assert all(map(lambda cfg: cfg.n_series == n_series, configs))
        assert len(solver_results) % n_series == 0

        results: list[ExperimentResult] = []
        for solver_result_batch in iter_batched(solver_results, n_series):
            results.append(ExperimentResult(
                series_outputs=list(map(lambda res: res.series_output, solver_result_batch)),
                metadata=list(map(lambda res: res.run_metadata, solver_result_batch))
            ))
        return results


class AresExpScheduler:
    def __init__(self, solver: SolverProxy):
        self.solver = solver

    def run(self, configs: list[ExperimentConfig]) -> None:
        params = self._params_from_configs(configs)
        jobspec = ArrayJobSpec()
        indices = input_range_from_jobspec(jobspec, len(params))

        for i in indices:
            self.solver.run(params[i])

        return None

