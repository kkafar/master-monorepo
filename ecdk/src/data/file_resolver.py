from pathlib import Path
from typing import Iterable, Generator
import itertools as it


def enumerate_test_cases_in_dir(directory: Path) -> Generator[Path, None, None]:
    # Yep, that is it
    return directory.glob('*.txt')


def enumerate_result_files_in_dir(directory: Path) -> Generator[Path, None, None]:
    return directory.glob('*.txt')


def find_result_files_in_dir(directory: Path) -> list[Path]:
    return list(enumerate_result_files_in_dir(directory))


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


def resolve_all_input_files(input_files: list[Path] = [], recursive: bool = True) -> list[Path]:
    """ Joins `input_files` with all test cases found in `input_dirs` """
    if input_files is None:
        input_files = []

    all_files = list(filter(lambda file: file.is_file(), input_files))
    directories = list(filter(lambda file: file.is_dir(), input_files))

    file_resolver = find_test_cases_in_dir_recursive if recursive else find_test_cases_in_dir

    for input_dir in directories:
        all_files.extend(file_resolver(input_dir))

    print(all_files)

    return all_files

