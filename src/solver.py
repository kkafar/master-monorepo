import subprocess as sp
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SolverParams:
    input_file: Path
    output_file: Path


ExperimentResult = None


class SolverProxy:
    INPUT_FILE_OPT_NAME = '--input-file'
    OUTPUT_FILE_OPT_NAME = '--output-file'

    binary: Path

    def __init__(self, binary: Path):
        self.binary = binary

    def run(self, params: SolverParams) -> ExperimentResult:
        print(f"[SolverProxy] Running for {params}")
        completed_process = sp.CompletedProcess = sp.run([
            self.binary,
            SolverProxy.INPUT_FILE_OPT_NAME,
            params.input_file,
            SolverProxy.OUTPUT_FILE_OPT_NAME,
            params.output_file,
        ])

        if completed_process.returncode != 0:
            print("JSSP solver exited with non-zero return code")
            exit(completed_process.returncode)

        return None

