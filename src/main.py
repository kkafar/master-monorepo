import polars as pl
import matplotlib.pyplot as plt
import cli
import subprocess as sp
import os


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


configure_env()
args = cli.parse_cli_args()
run_solver(args)



# data_file = Path(sys.argv[1])
# assert data_file.is_file(), "Pointed file does not exist or is not a regular file"
#
# problem_name = None
# if len(sys.argv) > 2:
#     problem_name = sys.argv[2]
#
# data_df = pl.read_csv(data_file, has_header=False, new_columns=[
#                       "event", "gen", "time", "fitness"]).filter(pl.col('event') != 'diversity').select(pl.exclude('column_5'))
# print(data_df)
#
# fig, plot = plt.subplots(nrows=1, ncols=1)
# jssp.plot_fitness_improvements(data_df, plot)
# plot.set(
#     title="Najlepszy osobnik w populacji w danej generacji" +
#     f', problem: {problem_name}' if problem_name else "",
#     xlabel="Generacja",
#     ylabel="Wartość funkcji fitness"
# )
#
# plt.show()

