import subprocess as sp
import datetime as dt
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SolverParams:
    input_file: Path
    output_file: Path


@dataclass
class SolverResult:
    duration: dt.timedelta


class SolverProxy:
    INPUT_FILE_OPT_NAME = '--input-file'
    OUTPUT_FILE_OPT_NAME = '--output-file'

    binary: Path

    def __init__(self, binary: Path):
        self.binary = binary

    def run(self, params: SolverParams) -> SolverResult:
        print(f"[SolverProxy] Running with {params}", end=' ')
        start_time = dt.datetime.now()
        completed_process: sp.CompletedProcess = sp.run([
            self.binary,
            SolverProxy.INPUT_FILE_OPT_NAME,
            params.input_file,
            SolverProxy.OUTPUT_FILE_OPT_NAME,
            params.output_file,
        ], stdout=sp.DEVNULL)
        end_time = dt.datetime.now()

        if completed_process.returncode != 0:
            print(f"Failed with nonzero return code {completed_process.returncode}")
            exit(completed_process.returncode)

        timedelta: dt.timedelta = end_time - start_time
        print(f"Done in {timedelta}")
        return SolverResult(duration=timedelta)

