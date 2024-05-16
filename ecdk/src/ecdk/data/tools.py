import polars as pl
import core.fs
import json
from tqdm import tqdm
from typing import Dict, Optional
from pathlib import Path
from experiment.model import (
    ExperimentResult,
    Experiment,
    SeriesOutputMetadata,
    SolverDescription,
)
from data.model import (
    Col,
    Event,
    InstanceMetadata,
    JoinedExperimentData,
)
from core.series import load_series_output, materialize_series_output


def experiment_result_from_dir(directory: Path, materialize: bool = False) -> ExperimentResult:
    # Metadata collected by SolverProxy is not dumped on the disk currently.
    # TODO: dump it on the disk & load it here
    result = ExperimentResult([], None)
    for series_dir in filter(lambda file: file.is_dir(), directory.iterdir()):
        series_output = load_series_output(series_dir, lazy=not materialize)
        result.series_outputs.append(series_output)

    return result


def extract_experiment_results_from_dir(directory: Path, materialize: bool = False) -> list[ExperimentResult]:
    exp_results = []
    for exp_dir in filter(lambda file: file.is_dir(), directory.iterdir()):
        exp_results.append(experiment_result_from_dir(exp_dir, materialize))
    return exp_results


def experiment_from_dir(directory: Path, materialize: bool = False) -> Experiment:
    exp_file = core.fs.experiment_file_from_directory(directory)
    exp: Experiment = None
    with open(exp_file, 'r') as file:
        exp = json.load(file, object_hook=Experiment.from_dict)

    assert exp is not None, f"Failed to load experiment configuration data for {exp_file}"

    exp_result = experiment_result_from_dir(directory, materialize)
    exp.result = exp_result
    exp.batch_dir = directory.parent
    return exp


def extract_experiments_from_dir(directory: Path) -> list[Experiment]:
    print("Loading experiments output data into memory...", flush=True)
    return [
        experiment_from_dir(d) for d in tqdm(filter(lambda f: f.is_dir(), directory.iterdir()))
    ]


def data_frame_from_file(data_file: Path, has_header: bool = False) -> pl.DataFrame:
    df = (pl.read_csv(data_file,
                      has_header=has_header))
    return df


def __update_df_with(base_df: pl.DataFrame, new_df: pl.DataFrame) -> pl.DataFrame:
    if base_df is not None:
        base_df.vstack(new_df, in_place=True)
    else:
        base_df = new_df
    return base_df


def __add_sid_column_to_df(df: pl.DataFrame, sid: int) -> pl.DataFrame:
    return df.with_columns(pl.Series(Col.SID, [sid for _ in range(0, df.shape[0])]))


def _df_from_metadata(md: SeriesOutputMetadata) -> pl.DataFrame:
    return pl.DataFrame({
        'gen_count': md.generation_count,
        'total_time': md.total_time,
        'fitness': md.fitness,
        'hash': md.hash,

        # These might be None
        'age_avg': md.age_avg,
        'age_max': md.age_max,
        'indv_count': md.individual_count,
        'co_inv_max': md.crossover_involvement_max,
        'co_inv_min': md.crossover_involvement_min,
    })


def experiment_data_from_all_series(experiment: Experiment) -> JoinedExperimentData:
    exp_data = JoinedExperimentData(
        newbest=None,
        popmetrics=None,
        bestingen=None,
        popgentime=None,
        iterinfo=None,
        summarydf=None,
    )

    for sid, series_output in enumerate(experiment.result.series_outputs):
        if not series_output.is_materialized():
            materialize_series_output(series_output, force=False)

        # I've messed up some time ago and changed name (and structure) of the file, paying the debt here
        popmetrics_filename = Event.POP_METRICS if series_output.data.data_for_event(Event.POP_METRICS) is not None else Event.DIVERSITY

        exp_data.newbest = __update_df_with(exp_data.newbest, __add_sid_column_to_df(series_output.data.data_for_event(Event.NEW_BEST), sid))
        exp_data.popmetrics = __update_df_with(exp_data.popmetrics, __add_sid_column_to_df(series_output.data.data_for_event(popmetrics_filename), sid))
        exp_data.bestingen = __update_df_with(exp_data.bestingen, __add_sid_column_to_df(series_output.data.data_for_event(Event.BEST_IN_GEN), sid))
        exp_data.popgentime = __update_df_with(exp_data.popgentime, __add_sid_column_to_df(series_output.data.data_for_event(Event.POP_GEN_TIME), sid))
        exp_data.iterinfo = __update_df_with(exp_data.iterinfo, __add_sid_column_to_df(series_output.data.data_for_event(Event.ITER_INFO), sid))
        exp_data.summarydf = __update_df_with(exp_data.summarydf, __add_sid_column_to_df(_df_from_metadata(series_output.data.metadata), sid))

    return exp_data


def maybe_load_instance_metadata(metadata_file: Optional[Path]) -> Optional[Dict[str, InstanceMetadata]]:
    if metadata_file is None:
        return None
    df: pl.DataFrame = data_frame_from_file(metadata_file, has_header=True)
    metadata_store = {}
    for record in df.iter_rows():
        metadata = InstanceMetadata(*record)
        metadata_store[metadata.id] = metadata
    return metadata_store


def extract_solver_desc_from_experiment_batch(batch: list[Experiment]) -> Optional[tuple[SolverDescription, str]]:
    assert len(batch) > 0, "Can not extract solver desc, because batch is empty"
    exp = batch[0]

    assert exp.result is not None, "Can not extract solver desc, because exp has no result"
    assert len(exp.result.series_outputs) > 0, "Can not extract solver desc, because there are no series outputs"
    series_output = exp.result.series_outputs[0]
    logfile = series_output.files.logfile

    assert logfile is not None, "Can not extract solver desc, because logfile is None"
    assert logfile.is_file(), f"Can not extract solver desc, because given logfile {logfile} is not a file"

    return _parse_solver_description_from_file(logfile)


def _parse_solver_description_from_file(file: Path) -> Optional[tuple[SolverDescription, str]]:
    start_marker = "BEGIN_SOLVER_DESC"
    end_marker = "END_SOLVER_DESC"

    json_str = None

    # print('parsing')
    with open(file, 'r') as fd:
        while (line := fd.readline()) != '':
            if not line.startswith(start_marker):
                continue
            break
        else:
            return None

        buffer = []

        while not (json_line := fd.readline()).startswith(end_marker):
            buffer.append(json_line)

        json_str = ''.join(buffer)

    if not json_str:
        return None

    desc = json.loads(json_str, object_hook=SolverDescription.from_dict)
    return desc, json_str

