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


class SolverProxy:
    INPUT_FILE_OPT_NAME = '--input-file'
    OUTPUT_DIR_OPT_NAME = '--output-dir'

    def __init__(self, binary: Path):
        self.binary: Path = binary

    def run(self, params: SolverParams) -> SolverResult:
        print(f"[SolverProxy] Running with {params}", end=' ', flush=True)
        start_time = dt.datetime.now()
        completed_process: sp.CompletedProcess = sp.run([
            self.binary,
            SolverProxy.INPUT_FILE_OPT_NAME,
            params.input_file,
            SolverProxy.OUTPUT_DIR_OPT_NAME,
            params.output_dir,
        ], stdout=sp.DEVNULL)
        end_time = dt.datetime.now()

        if completed_process.returncode != 0:
            print(f"Failed with nonzero return code {completed_process.returncode}")
            exit(completed_process.returncode)

        timedelta: dt.timedelta = end_time - start_time
        print(f"Done in {timedelta}")

        return SolverResult(
            series_output=load_series_output(params.output_dir, lazy=True),
            run_metadata=SolverRunMetadata(duration=timedelta))

    def run_nonblocking(self, params: list[SolverParams], process_limit: int = 1, poll_interval: int = 1) -> list[SolverResult]:
        processes = set()
        n_scheduled = min(process_limit, len(params))
        start_time = dt.datetime.now()

        for p in params[:n_scheduled]:
            print(f"[SolverProxy] Running with {p}", flush=True)
            processes.add(sp.Popen([
                self.binary,
                SolverProxy.INPUT_FILE_OPT_NAME,
                p.input_file,
                SolverProxy.OUTPUT_DIR_OPT_NAME,
                p.output_dir,
            ], stdout=sp.DEVNULL))

        should_loop = n_scheduled < len(params)

        new_processes = set()
        to_remove = set()
        while should_loop:
            new_processes.clear()
            to_remove.clear()

            for proc in processes:
                ret_code = proc.poll()
                if ret_code is not None and n_scheduled < len(params):
                    if ret_code != 0:
                        print(f"[SolverProxy][ERROR] Proc with args {proc.args} failed with nonzero return code {ret_code}")

                    to_remove.add(proc)
                    param = params[n_scheduled]

                    print(f"[SolverProxy] Running with {param}", flush=True)
                    new_processes.add(sp.Popen([
                        self.binary,
                        SolverProxy.INPUT_FILE_OPT_NAME,
                        param.input_file,
                        SolverProxy.OUTPUT_DIR_OPT_NAME,
                        param.output_dir,
                    ], stdout=sp.DEVNULL))
                    n_scheduled += 1

            processes.difference_update(to_remove)
            processes.update(new_processes)

            if n_scheduled >= len(params):
                break

            sleep(poll_interval)

        for proc in processes:
            proc.wait()

        end_time = dt.datetime.now()
        timedelta: dt.timedelta = end_time - start_time
        print(f"[SolverProxy] Completed batch of {len(params)} in {timedelta}")
        return [SolverResult(series_output=load_series_output(p.output_dir, lazy=True),
                             run_metadata=SolverRunMetadata(duration=timedelta)) for p in params]

