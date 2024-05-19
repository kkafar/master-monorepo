import subprocess as sp
import datetime as dt
from pathlib import Path
from typing import Optional
from .model import (
    SolverParams,
    SolverResult,
    SolverRunMetadata,
)
from core.series import load_series_output
from core.version import Version


class SolverProxy:
    INPUT_FILE_OPT = '--input-file'
    OUTPUT_DIR_OPT = '--output-dir'
    CONFIG_FILE_OPT = '--config'
    VERSION_OPT = '--version'

    def __init__(self, binary: Path, version: Optional[Version] = None):
        self.binary: Path = binary
        self._cached_version: Optional[Version] = version

    # def __task_from_params(self, id: int, params: SolverParams) -> Task:
    #     return Task(
    #         id=id,
    #         process_args=self.exec_cmd_from_params(params),
    #         stdout_file=params.stdout_file
    #     )

    def exec_cmd_from_params(self, params: SolverParams, stringify_args: bool = False) -> list[str]:
        base = [
            self.binary,
            SolverProxy.INPUT_FILE_OPT,
            params.input_file,
            SolverProxy.OUTPUT_DIR_OPT,
            params.output_dir
        ]
        if params.config_file is not None:
            base.extend((SolverProxy.CONFIG_FILE_OPT, params.config_file))

        if stringify_args:
            # For older versions of Python on Ares / HyperQueue
            base = list(map(str, base))

        return base

    def _query_version_cmd(self, stringify_args: bool = False) -> list[str]:
        cmd_parts = [
            self.binary,
            SolverProxy.VERSION_OPT
        ]
        return cmd_parts

        if stringify_args:
            # For older versions of Python on Ares / HyperQueue
            cmd_parts = list(map(str, cmd_parts))

    def run(self, params: SolverParams) -> SolverResult:
        print(f"Running with {params}", end=' ', flush=True)
        start_time = dt.datetime.now()
        args = self.exec_cmd_from_params(params)
        completed_process: sp.CompletedProcess = sp.run(args, stdout=sp.DEVNULL)
        end_time = dt.datetime.now()

        timedelta: dt.timedelta = end_time - start_time

        if completed_process.returncode != 0:
            print(f"Failed with nonzero return code {completed_process.returncode}")
            # exit(completed_process.returncode)
        else:
            print(f"Done in {timedelta}")

        return SolverResult(
            series_output=load_series_output(params.output_dir, lazy=True),
            run_metadata=SolverRunMetadata(duration=timedelta, status=completed_process.returncode))

    # def run_multiprocess(self, params: Iterable[SolverParams], process_limit: int = 1, poll_interval: float = 0.1) -> list[SolverResult]:
    #     tasks = list(map(lambda x: self.__task_from_params(x[0], x[1]), enumerate(params)))
    #     completed_tasks, runinfo = MultiProcessTaskRunner().run(tasks, process_limit, poll_interval)
    #
    #     return [SolverResult(
    #         series_output=load_series_output(param.output_dir, lazy=True),
    #         run_metadata=SolverRunMetadata(  # Propagate more information from completed taks here
    #             duration=compl_task.duration,
    #             status=compl_task.return_code
    #         )
    #     ) for param, compl_task in zip(params, completed_tasks)]

    def _query_version(self) -> Optional[Version]:
        args = self._query_version_cmd()
        completed_process: sp.CompletedProcess = sp.run(args, capture_output=True, encoding="utf-8")
        maybe_version_information = completed_process.stdout
        # TODO: consider running some validation here & handling errors
        version = Version.from_str(maybe_version_information)
        return version

    def version(self) -> Optional[Version]:
        if self._cached_version is not None:
            return self._cached_version

        self._cached_version = self._query_version()
        return self._cached_version


