import hashlib
import itertools as it
from pathlib import Path
from typing import TypeAlias, Generator, Iterable
from core.fs import (
    get_solutions_dir_for_experiment_family,
    experiment_family_from_solution_dir,
    experiment_id_from_solution_file,
)
from experiment.model import (ExperimentId, ExperimentFamily, SolutionHash, SolutionStr)


RawSolutionDataRecord: TypeAlias = tuple[ExperimentId, SolutionHash, SolutionStr]
RawSolutionDataGenerator: TypeAlias = Generator[RawSolutionDataRecord, None, None]


class RawSolutionDataProvider:
    """ Raw solution data for given experiment consists of solution strings,
    each solution string is put in separate line and operations inside a given solution
    string are space separated. This class exposes generator to stream data for all experiment
    families requested.
    """

    def __init__(self, solution_data_dir: Path, considered_experiment_families: Iterable[ExperimentFamily] = ('ft', 'la')):
        assert solution_data_dir is not None, "Provided solution data dir must not be None"
        assert solution_data_dir.is_dir(), f"Provided solution data dir: {solution_data_dir} is not a directory"

        self._solution_data_base_dir: Path = solution_data_dir
        self._families: Iterable[ExperimentFamily] = considered_experiment_families

    def get_all_solution_data(self) -> RawSolutionDataGenerator:
        generators = (
            gen for gen in (self._generate_experiment_family_data(family) for family in self._families)
        )
        for gen in generators:
            for record in gen:
                yield record

    def _generate_experiment_family_data(self, family: ExperimentFamily) -> RawSolutionDataGenerator:
        family_dir = get_solutions_dir_for_experiment_family(self._solution_data_base_dir, family)
        for file in filter(lambda f: f.name.endswith("solutions.txt"), family_dir.iterdir()):
            for record in self._enumerate_raw_data_records(file):
                yield record

    def _enumerate_raw_data_records(self, raw_data_file: Path) -> RawSolutionDataGenerator:
        experiment_id = experiment_id_from_solution_file(raw_data_file)
        with open(raw_data_file, mode='r') as file:
            for line in file:
                yield (experiment_id, *self._process_raw_data_line(line))

    def _process_raw_data_line(self, line: str) -> tuple[SolutionHash, SolutionStr]:
        solution_str: SolutionStr = line.strip().replace('\t', '_')
        solution_hash = hashlib.md5(solution_str.encode('utf-8')).hexdigest()
        return (solution_hash, solution_str)

