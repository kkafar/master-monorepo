import polars as pl
import matplotlib.pyplot as plt
from typing import Dict, Iterable, Optional
from pathlib import Path
from experiment.model import ExperimentResult, ExperimentConfig, Experiment
from .file_resolver import find_result_files_in_dir
from collections import defaultdict
from data.model import (
    Col,
    Event,
    EventConfig,
    config_for_event,
    EventName,
    InstanceMetadata
)
from .plot import (
    plot_diversity,
    plot_best_in_gen
)


def partition_exp_by_files(paths: list[Path]) -> Dict[str, list[Path]]:
    exp_to_files = defaultdict(list)

    for exp_file in paths:
        partitioned_name: list[str] = exp_file.stem.split('-')
        exp_name = '-'.join(partitioned_name[0:partitioned_name.index('result')])
        exp_to_files[exp_name].append(exp_file)

    return exp_to_files


def extract_experiment_results_from_dir(directory: Path) -> list[ExperimentResult]:
    all_result_files = find_result_files_in_dir(directory)
    experiment_raw_results = partition_exp_by_files(all_result_files)

    experiment_results = []
    for name, paths in experiment_raw_results.items():
        experiment_results.append(
            ExperimentResult(
                ExperimentConfig(
                    name=name,
                    input_file='unknown',
                    output_dir=directory,
                    repeats_no=len(paths)
                ),
                None,
                paths
            )
        )
    return experiment_results


def data_frame_from_file(data_file: Path, has_header: bool = False) -> pl.DataFrame:
    df = (pl.read_csv(data_file,
                      has_header=has_header))
    return df


def extract_data_for_event_with_config(data: pl.DataFrame, config: EventConfig) -> pl.DataFrame:
    selected_columns = [data.columns[i] for i in config.raw_columns]
    df = (data
          .filter(pl.col(Col.EVENT) == config.name)
          .select(selected_columns))
    df.columns = config.record_schema
    return df


def partition_experiment_data_by_event(data: pl.DataFrame) -> dict[EventName, pl.DataFrame]:
    return {
        event_name: extract_data_for_event_with_config(data, config_for_event(event_name))
        for event_name in Event.ALL_EVENTS
    }


def join_data_from_multiple_runs(output_files: Iterable[Path]) -> pl.DataFrame:
    main_df: Optional[pl.DataFrame] = None
    for sid, data_file in enumerate(output_files):
        print(f'Processing data file {data_file} sid {sid}')
        tmp_df: pl.DataFrame = data_frame_from_file(data_file)
        series_column = pl.Series("sid", [sid for _ in range(tmp_df.height)])
        tmp_df = tmp_df.with_columns(series_column).rename({'column_1': Col.EVENT})
        if main_df is not None:
            main_df.vstack(tmp_df, in_place=True)
        else:
            main_df = tmp_df
    return main_df


def process_experiment_data(data: pl.DataFrame, exp: Experiment):
    print(f"Processing experiment {exp.name}")
    partitioned_data = partition_experiment_data_by_event(data)

    # TODO: Extract these to separate functions

    fig, plot = plt.subplots(nrows=1, ncols=1)
    plot_best_in_gen(partitioned_data.get(Event.BEST_IN_GEN), plot)
    plot.set(
        title=f"Best fitness by generation, {exp.name}",
        xlabel="Generation",
        ylabel="Fitness value"
    )
    plot.legend()

    fig, plot = plt.subplots(nrows=1, ncols=1)
    plot_diversity(partitioned_data.get(Event.DIVERSITY), plot)
    plot.set(
        title=f"Diversity rate by generation, {exp.name}",
        xlabel="Generation",
        ylabel="Diversity rate"
    )
    plot.legend()
    plt.show()


def process_experiment_batch_output(batch: list[Experiment]):
    print(batch)
    for exp in batch:
        print(f'Processing {exp.name}')
        experiment_data = join_data_from_multiple_runs(exp.run_result.output_files)
        process_experiment_data(experiment_data, exp)
        break


def maybe_load_instance_metadata(metadata_file: Optional[Path]) -> Optional[Dict[str, InstanceMetadata]]:
    if metadata_file is None:
        return None
    df: pl.DataFrame = data_frame_from_file(metadata_file, has_header=True)
    metadata_store = {}
    for record in df.iter_rows():
        metadata = InstanceMetadata(*record)
        metadata_store[metadata.id] = metadata
    return metadata_store

