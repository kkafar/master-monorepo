import polars as pl
import matplotlib.pyplot as plt
import jssp
from pathlib import Path
from experiment.runner import ExperimentResult
from data.model import Col, Event, EventConfig, config_for_event
from typing import Iterable, Optional
from pprint import pprint


def data_frame_from_file(data_file: Path) -> pl.DataFrame:
    df = (pl.read_csv(data_file,
                      has_header=False))
    return df


def extract_data_for_event_with_config(data: pl.DataFrame, config: EventConfig) -> pl.DataFrame:
    selected_columns = [data.columns[i] for i in config.raw_columns]
    df = (data
          .filter(pl.col(Col.EVENT) == config.name)
          .select(selected_columns))
    df.columns = config.record_schema
    print(df)
    return df


def join_data_from_multiple_runs(output_files: Iterable[Path]) -> pl.DataFrame:
    main_df: Optional[pl.DataFrame] = None
    for sid, data_file in enumerate(output_files):
        print(f'Processing data file {data_file} sid {sid}')
        tmp_df: pl.DataFrename = data_frame_from_file(data_file)
        series_column = pl.Series("sid", [sid for _ in range(tmp_df.height)])
        tmp_df = tmp_df.with_columns(series_column).rename({'column_1': Col.EVENT})
        if main_df is not None:
            main_df.vstack(tmp_df, in_place=True)
        else:
            main_df = tmp_df
    return main_df


class RawDataProcessor:
    def __init__(self):
        pass


def load_data(data_file: Path) -> pl.DataFrame:
    data_df = (pl.read_csv(data_file, has_header=False, new_columns=Col.ALL_COLLS)
               .filter(pl.col(Col.EVENT) != Event.DIVERSITY)
               .select(pl.exclude('column_5')))
    return data_df


def process_output(output_dir: Path):
    for output_file in output_dir.glob('*.txt'):
        process_data(output_file)


def process_data(input_file: Path):
    data_df = load_data(input_file)
    problem_name = None

    fig, plot = plt.subplots(nrows=1, ncols=1)
    jssp.plot_fitness_improvements(data_df, plot)
    plot.set(
        title="Najlepszy osobnik w populacji w danej generacji" +
        f', problem: {problem_name}' if problem_name else "",
        xlabel="Generacja",
        ylabel="Wartość funkcji fitness"
    )
    plt.show()


def process_experiment_data(experiment_data: pl.DataFrame):
    # 1. Split into
    pass


def process_experiment_results(exp_results: list[ExperimentResult]):
    for result in exp_results:
        print(f'Processing {result.description.name}')
        pprint(result.output_files)
        experiment_data = join_data_from_multiple_runs(result.output_files)
        for event_name in Event.ALL_EVENTS:
            extract_data_for_event_with_config(experiment_data, config_for_event(event_name))
        break

