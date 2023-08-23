import polars as pl
import matplotlib.pyplot as plt
import cli
import subprocess as sp
import logging
import jssp
import model
from config import Config
from pathlib import Path
from typing import Iterable
from runner import ExperimentRunner
from solver import SolverProxy


def configure_env():
    pl.Config.set_tbl_rows(400)
    pl.Config.set_tbl_cols(10)
    plt.rcParams['figure.figsize'] = (16, 9)


def resolve_output_file_name(output_dir: Path, input_file: Path, output_file_suffix: Path, joiner: str = '-') -> str:
    assert output_file_suffix is not None
    return output_dir.joinpath(input_file.stem + joiner + output_file_suffix + input_file.suffix)


def run_solver(binary: Path, input_file: Path, output_file: Path):
    completed_pc: sp.CompletedProcess = sp.run([binary, '--input-file', input_file, '--output-file', output_file])
    if completed_pc.returncode != 0:
        print("Jssp solver exited with non-zero return code")
        exit(completed_pc.returncode)


def run_solver_for_many_inputs(binary: Path, input_files: Iterable[Path], output_dir: Path, output_file_suffix: str = 'log'):
    for input_file in input_files:
        run_solver(binary, input_file, resolve_output_file_name(output_dir, input_file, output_file_suffix))


def load_data(data_file: Path) -> pl.DataFrame:
    data_df = (pl.read_csv(data_file, has_header=False, new_columns=model.OUTPUT_LABELS)
               .filter(pl.col(model.COL_EVENT) != 'diversity')
               .select(pl.exclude('column_5')))
    return data_df


def process_output(output_dir: Path):
    for output_file in output_dir.glob('*.txt'):
        process_data(output_file)


def process_data(input_file: Path):
    data_df = load_data(input_file)
    print(data_df)

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


def resolve_input_files_in_dir(directory: Path) -> Iterable[Path]:
    return directory.glob('*.txt')


def resolve_all_input_files(args: cli.Args) -> list[Path]:
    all_paths = args.input_files if args.input_files is not None else []
    if args.input_dirs is not None:
        for input_dir in args.input_dirs:
            all_paths.extend(resolve_input_files_in_dir(input_dir))

    return all_paths


def main():
    configure_env()
    args = cli.parse_cli_args()
    runner = ExperimentRunner(SolverProxy(args.bin), Config(resolve_all_input_files(args), args.output_file, args.output_dir))
    runner.run()


if __name__ == "__main__":
    main()

