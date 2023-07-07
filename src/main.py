import polars as pl
import matplotlib.pyplot as plt
import cli
import subprocess as sp
import jssp
import model
from pathlib import Path


def configure_env():
    pl.Config.set_tbl_rows(400)
    pl.Config.set_tbl_cols(10)
    plt.rcParams['figure.figsize'] = (16, 9)


def run_solver(args: cli.Args):
    assert args.input_file is not None
    completed_pc: sp.CompletedProcess = sp.run([args.bin, '--input-file', args.input_file, '--output-file', args.output_file])
    if completed_pc.returncode != 0:
        print("Jssp solver exited with non-zero return code")
        exit(completed_pc.returncode)


def load_data(file: Path) -> pl.DataFrame:
    data_df = (pl.read_csv(data_file, has_header=False, new_columns=model.OUTPUT_LABELS)
               .filter(pl.col(model.COL_EVENT) != 'diversity')
               .select(pl.exclude('column_5')))
    return data_df


configure_env()
args = cli.parse_cli_args()
run_solver(args)

data_file = args.output_file
assert data_file.is_file(), f"Solver did not produce valid data output file under path: {data_file}"

data_df = load_data(data_file)
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

