from typing import Dict, Iterable
from pathlib import Path
from experiment.model import (
    SeriesOutputFiles,
    SeriesOutputData,
    SeriesOutput,
)
from core.util import find_first_or_none
from core.conversion import deserialize_series_metadata_from_dict
import polars as pl
import json


def __event_file_filter(file: Path) -> bool:
    return file.stem.startswith("event_")


def __run_metadata_file_filter(file: Path) -> bool:
    return file.stem == "run_metadata"


def __solver_logfile_filter(file: Path) -> bool:
    return file.stem.startswith('stdout')


def _event_name_from_data_file(event_data_file: Path) -> str:
    return event_data_file.stem.split('_')[1]


def _event_file_map_from_data_files(event_files: Iterable[Path]) -> Dict[str, Path]:
    return {
        _event_name_from_data_file(file): file
        for file in event_files
    }


def _load_series_metadata_from_file(metadata_file: Path) -> SeriesOutputFiles:
    metadata = None

    with open(metadata_file, 'r') as file:
        metadata = json.load(file, object_hook=deserialize_series_metadata_from_dict)

    return metadata


def _load_series_data_from_files(files: SeriesOutputFiles) -> SeriesOutputData:
    data: Dict[str, pl.DataFrame] = dict()

    for event_name, file in files.event_files.items():
        data[event_name] = pl.read_csv(file, has_header=True)

    metadata = _load_series_metadata_from_file(files.run_metadata_file)

    return SeriesOutputData(data, metadata)


def _resolve_series_files_from_dir(directory: Path) -> SeriesOutputFiles:
    all_files = list(filter(lambda file: file.is_file(), directory.iterdir()))
    assert len(all_files) > 0, f"Ill formed series result - no files found in directory {directory}"

    event_files = _event_file_map_from_data_files(filter(__event_file_filter, all_files))
    run_metadata_file = find_first_or_none(all_files, __run_metadata_file_filter)
    logfile = find_first_or_none(all_files, __solver_logfile_filter)
    assert run_metadata_file is not None, "There must be metadata attached to experiment result"

    return SeriesOutputFiles(directory, event_files, run_metadata_file, logfile)


def materialize_series_output(output: SeriesOutput, force: bool = False):
    if output.data is None or force:
        output.data = _load_series_data_from_files(output.files)


def materialize_all_series_outputs(outputs: list[SeriesOutput], force: bool = False):
    """ :param force tells whether the data should be loaded even if there is a dataframe attached
    to an object already """
    for output in outputs:
        materialize_series_output(output, force)


def load_series_output(directory: Path, lazy: bool = False) -> SeriesOutput:
    files = _resolve_series_files_from_dir(directory)
    series_output = SeriesOutput(None, files)
    if not lazy:
        materialize_series_output(series_output)
    return series_output

