import itertools as it
from typing import Generator, Iterable
from .solver import SolverProxy, SolverParams, SolverRunMetadata, SolverResult
from .model import ExperimentResult, ExperimentConfig, SeriesOutput
from core.util import iter_batched
from core.fs import output_dir_for_series, solver_logfile_for_series
from core.env import ArrayJobSpec, input_range_from_jobspec


def solver_params_from_exp_config(config: ExperimentConfig) -> Generator[SolverParams, None, None]:
    for series_id in range(0, config.n_series):
        series_outdir = output_dir_for_series(config.output_dir, series_id)
        solver_logfile = solver_logfile_for_series(config.output_dir, series_id)
        yield SolverParams(config.input_file, series_outdir, config.config_file, solver_logfile)


def solver_params_from_exp_config_collection(config_coll: Iterable[ExperimentConfig]) -> Iterable[SolverParams]:
    return it.chain.from_iterable((solver_params_from_exp_config(config) for config in config_coll))


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
            return self.runner.run_multiprocess(self.configs, process_limit)


class LocalExperimentRunner:
    def __init__(self, solver: SolverProxy):
        self.solver: SolverProxy = solver


    def run(self, config: ExperimentConfig) -> ExperimentResult:
        run_metadata: list[SolverRunMetadata] = []
        series_outputs: list[SeriesOutput] = []
        for params in solver_params_from_exp_config(config):
            solver_result: SolverResult = self.solver.run(params)
            series_outputs.append(solver_result.series_output)
            run_metadata.append(solver_result.run_metadata)
        return ExperimentResult(series_outputs=series_outputs, metadata=run_metadata)


    def run_multiprocess(self, configs: Iterable[ExperimentConfig], process_limit: int = 1) -> list[ExperimentResult]:
        params_iter = solver_params_from_exp_config_collection(configs)

        solver_results = self.solver.run_multiprocess(params_iter, process_limit)

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
        params = [param for param in solver_params_from_exp_config_collection(configs)]
        jobspec = ArrayJobSpec()
        indices = input_range_from_jobspec(jobspec, len(params))

        for i in indices:
            self.solver.run(params[i])

        return None


class HyperQueueRunner:
    def __init__(self, solver: SolverProxy):
        import hyperqueue as hq
        self._solver: SolverProxy = solver
        self._client = hq.Client()  # We try to create client from default options, not passing path to server files rn


    def run(self, configs: list[ExperimentConfig]) -> None:
        import hyperqueue as hq
        # Important thing here is that we only dispatch the jobs, without waiting for their completion, at for least now
        params_iter = solver_params_from_exp_config_collection(configs)

        # We run on single job as the scheduling can be done on task level
        job = hq.Job(max_fails=1)

        for id, params in enumerate(params_iter):
            # With current implemntation this will be True, however it is not guaranteed in general
            if params.stdout_file is not None:
                job.program(self._solver.exec_cmd_from_params(params, stringify_args=True),
                            name=f'Task_{id}',
                            stdout=params.stdout_file,
                            stderr=params.stdout_file)
            else:
                job.program(self._solver.exec_cmd_from_params(params, stringify_args=True), name=f'Task_{id}')

        self._client.submit(job)


