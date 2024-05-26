import sqlite3 as sql
from pathlib import Path
from typing import Iterable
from .raw_data_provider import RawSolutionDataProvider
from core.util import iter_batched
from experiment.model import SolutionHash, ExperimentId


class DatabaseProxy:
    TRANSACTION_BATCH_SIZE = 64

    def __init__(self, db_path: Path, base_solutions_dir: Path, create_index: bool = True):
        # I need to know whether the database existed or not to know whether
        # there is a need to populate it or not.

        self._db_path: Path = db_path

        # Here we miss the case, when the file exists and is not a database,
        # or exists, but the database is empty. We can do it better,
        # e.g. by inspecting db schema or sth.
        needs_to_be_populated = not db_path.is_file()
        self._connection: sql.Connection = sql.connect(database=str(db_path))

        if needs_to_be_populated:
            self._create_tables()
            self._populate_with_reference_data(base_solutions_dir)
            if create_index:
                self._create_index()

    def _create_tables(self):
        self._connection.cursor().execute("""
                       CREATE TABLE IF NOT EXISTS solution_reference(
                           experiment_id TEXT NOT NULL,
                           solution_hash TEXT NOT NULL,
                           solution_str TEXT NOT NULL,
                           PRIMARY KEY (experiment_id, solution_hash)
                       );
                       """)
        self._connection.commit()

    def _create_index(self):
        self._connection.cursor().execute(
            """
            CREATE UNIQUE INDEX idx_solution_reference_hash ON solution_reference (solution_hash);
            """
        )
        self._connection.commit()

    def _populate_with_reference_data(self, base_solutions_dir: Path):
        print('Populating DB with reference data (this might take a while)...')
        cursor = self._connection.cursor()
        for record in iter_batched(RawSolutionDataProvider(base_solutions_dir).get_all_solution_data(), DatabaseProxy.TRANSACTION_BATCH_SIZE):
            cursor = cursor.executemany("INSERT INTO solution_reference (experiment_id, solution_hash, solution_str) VALUES(?, ?, ?);", record)
        self._connection.commit()

    def has_reference_solution_hashes(self, solution_hashes: Iterable[SolutionHash]) -> list[tuple[ExperimentId, SolutionHash]]:
        cursor = self._connection.cursor()
        for hash in solution_hashes:
            cursor = cursor.execute(
                """
                SELECT experiment_id, solution_hash FROM solution_reference WHERE solution_hash = ?
                """,
                (hash,)
            )

        return cursor.fetchall()
