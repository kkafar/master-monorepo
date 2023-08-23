from solver import SolverProxy
from config import Config


class ExperimentRunner:
    solver: SolverProxy
    config: Config

    def __init__(self, solver: SolverProxy, config: Config):
        self.solver = solver
        self.config = config

    def run(self):
        for params in self.config.configurations:
            self.solver.run(params)

