from solver import SolverProxy, SolverParams, SolverResult
from config import ExpConfig
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ExpResult:
    name: str
    params: SolverParams
    run_results: list[SolverResult]


class ExpRunner:
    solver: SolverProxy
    config: ExpConfig

    def __init__(self, solver: SolverProxy, config: ExpConfig):
        self.solver = solver
        self.config = config

    def run(self) -> list[ExpResult]:
        results: list[ExpResult] = []
        for params in self.config.configurations:
            name = self.exp_name_from_input_file(params.input_file)
            run_result = self.solver.run(params)
            results.append(ExpResult(name, params, [run_result]))
        return results

    def exp_name_from_input_file(self, input_file: Path) -> str:
        return input_file.stem

