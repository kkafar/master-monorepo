from pathlib import Path
from typing import Iterable, Generator
import itertools as it


def enumerate_test_cases_in_dir(directory: Path) -> Iterable[Path]:
    # Yep, that is it
    return directory.glob('*.txt')


def enumerate_test_cases_in_dir_recursive(directory: Path) -> Iterable[Path]:
    """ Checks also subdirectories recursively """
    def helper(directory: Path, iterables: list[Generator[Path]] = []):
        iterables.append(enumerate_test_cases_in_dir(directory))
        for subdir in filter(lambda file: file.is_dir(), directory.iterdir()):
            helper(subdir, iterables)

    iterables = []
    helper(directory, iterables)
    return it.chain.from_iterable(iterables)


def find_test_cases_in_dir(directory: Path) -> list[Path]:
    return list(enumerate_test_cases_in_dir(directory))


def find_test_cases_in_dir_recursive(directory: Path) -> list[Path]:
    return list(enumerate_test_cases_in_dir_recursive(directory))
