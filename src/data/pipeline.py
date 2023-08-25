import polars as pl
import matplotlib.pyplot as plt
import jssp
from pathlib import Path
from experiment.runner import ExperimentResult
from model import Col, Event
from typing import Iterable, Optional
from pprint import pprint


def data_frame_from_file(data_file: Path) -> pl.DataFrame:
    df = (pl.scan_csv(data_file,
                      has_header=False,
                      infer_schema_length=None))
    return df


def join_data_from_multiple_runs(output_files: Iterable[Path]) -> pl.DataFrame:
    main_df: Optional[pl.DataFrame] = None
    for sid, data_file in enumerate(output_files):
        print(f'Processing data file {data_file} sid {sid}')
        tmp_df: pl.DataFrame = data_frame_from_file(data_file).collect()
        series_column = pl.Series([sid for _ in range(tmp_df.height)])
        tmp_df = tmp_df.with_columns(series_column.alias("sid"))
        if main_df is not None:
            main_df.vstack(tmp_df, in_place=True)
        else:
            main_df = tmp_df
    print(main_df)


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
    # print(data_df)

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


def process_experiment_results(exp_results: list[ExperimentResult]):
    for result in exp_results:
        print(f'Processing {result.description.name}')
        pprint(result.output_files)
        join_data_from_multiple_runs(result.output_files)
        break

