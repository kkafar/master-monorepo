import subprocess as sp
import datetime as dt
from pathlib import Path
from time import sleep
from .model import (
    SolverParams,
    SolverResult,
    SolverRunMetadata,
)
from core.series import load_series_output
from dataclasses import dataclass


@dataclass
class ScheduledProcess:
    params_id: int
    process: sp.Popen
    schedule_time: dt.datetime
    finish_time: dt.datetime = None

    def __eq__(self, other):
        return self.params_id == other.params_id

    def __hash__(self):
        return self.params_id

    def duration(self) -> dt.timedelta:
        return self.finish_time - self.schedule_time


class SolverProxy:
    INPUT_FILE_OPT_NAME = '--input-file'
    OUTPUT_DIR_OPT_NAME = '--output-dir'
    CONFIG_FILE_OPT_NAME = '--config'

    def __init__(self, binary: Path):
        self.binary: Path = binary

    def _run_args_from_params(self, params: SolverParams) -> list[str]:
        base = [
            str(self.binary),  # Converted for older version of Python on Ares
            SolverProxy.INPUT_FILE_OPT_NAME,
            params.input_file,
            SolverProxy.OUTPUT_DIR_OPT_NAME,
            params.output_dir
        ]
        if params.config_file is not None:
            base.extend((SolverProxy.CONFIG_FILE_OPT_NAME, params.config_file))
        return base

    def _log_run_start(self, id: int, p: SolverParams):
        print(f"Running id: {id}, input_file: {p.input_file}, output_dir: {p.output_dir}", flush=True)

    def _log_run_finish(self, id: int, proc: ScheduledProcess, finished_count: int, total_count: int):
        complete_percent = (finished_count / total_count) * 100
        print(f"Finished id: {id} at {proc.finish_time} in aprox. {proc.duration()} | {finished_count}/{total_count} ({complete_percent:.2f}%) ", flush=True)

    def _log_run_error(self, id: int, proc: ScheduledProcess):
        print(f"[ERROR] Proc with args {proc.process.args} failed with nonzero return code {proc.process.returncode}", flush=True)

    def run(self, params: SolverParams) -> SolverResult:
        print(f"Running with {params}", end=' ', flush=True)
        start_time = dt.datetime.now()
        args = self._run_args_from_params(params)
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

    def run_nonblocking(self, params: list[SolverParams], process_limit: int = 1, poll_interval: float = 0.1) -> list[SolverResult]:
        finished_count = 0
        running_procs = set()
        n_procs = len(params)
        n_scheduled = min(process_limit, n_procs)

        start_time = dt.datetime.now()

        for i, p in enumerate(params[:n_scheduled]):
            self._log_run_start(i, p)
            args = self._run_args_from_params(p)
            running_procs.add(ScheduledProcess(
                params_id=i,
                process=sp.Popen(args, stdout=sp.DEVNULL),
                schedule_time=dt.datetime.now()
            ))

        newly_scheduled_procs = set()
        recently_finished_procs = set()
        all_finished_procs = [-1 for _ in range(n_procs)]
        while True:
            newly_scheduled_procs.clear()
            recently_finished_procs.clear()

            for proc in running_procs:
                ret_code = proc.process.poll()

                # If this process has not completed yet, let it run
                if ret_code is None:
                    continue

                # The process has finished
                proc.finish_time = dt.datetime.now()
                recently_finished_procs.add(proc)
                all_finished_procs[proc.params_id] = proc
                finished_count += 1
                self._log_run_finish(proc.params_id, proc, finished_count, n_procs)

                if ret_code != 0:
                    self._log_run_error(proc.params_id, proc)

                # If there are any processes left to schedule
                if n_scheduled < n_procs:
                    param = params[n_scheduled]
                    self._log_run_start(n_scheduled, param)
                    args = self._run_args_from_params(param)
                    newly_scheduled_procs.add(ScheduledProcess(
                        params_id=n_scheduled,
                        process=sp.Popen(args, stdout=sp.DEVNULL),
                        schedule_time=dt.datetime.now()
                    ))

                    n_scheduled += 1

            running_procs.difference_update(recently_finished_procs)
            running_procs.update(newly_scheduled_procs)

            if len(running_procs) == 0:
                break
            else:
                sleep(poll_interval)

        end_time = dt.datetime.now()
        timedelta: dt.timedelta = end_time - start_time

        assert len(all_finished_procs) == n_procs

        print(f"Completed batch of {len(params)} in {timedelta}")
        return [SolverResult(series_output=load_series_output(p.output_dir, lazy=True),
                             run_metadata=SolverRunMetadata(duration=proc.duration(),
                                                            status=proc.process.returncode))
                for p, proc in zip(params, all_finished_procs)]

