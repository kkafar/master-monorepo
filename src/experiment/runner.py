from solver import SolverProxy, SolverParams
from config import ExpConfig
from dataclasses import dataclass


@dataclass
class ExpMetadata:
    duration: int


@dataclass
class ExpResult:
    name: str
    params: SolverParams
    meta: ExpMetadata


class ExpRunner:
    solver: SolverProxy
    config: ExpConfig

    def __init__(self, solver: SolverProxy, config: ExpConfig):
        self.solver = solver
        self.config = config

    def run(self):
        for params in self.config.configurations:
            self.solver.run(params)

