import polars as pl
import matplotlib.pyplot as plt
import cli
import data.file_resolver as fr
from config import Config
from runner import ExperimentRunner
from solver import SolverProxy


def configure_env():
    pl.Config.set_tbl_rows(400)
    pl.Config.set_tbl_cols(10)
    plt.rcParams['figure.figsize'] = (16, 9)


def main():
    configure_env()
    args = cli.parse_cli_args()
    runner = ExperimentRunner(SolverProxy(args.bin),
                              Config(fr.resolve_all_input_files(args),
                                     args.output_file, args.output_dir))
    runner.run()


if __name__ == "__main__":
    main()

