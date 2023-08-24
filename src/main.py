import polars as pl
import matplotlib.pyplot as plt
import cli
import data.file_resolver as fr
from experiment.config import ExpConfig
from experiment.runner import ExpRunner, ExpResult
from solver import SolverProxy


def configure_env():
    pl.Config.set_tbl_rows(400)
    pl.Config.set_tbl_cols(10)
    plt.rcParams['figure.figsize'] = (16, 9)


def main():
    configure_env()
    args = cli.parse_cli_args()
    runner = ExpRunner(SolverProxy(args.bin),
                       ExpConfig(fr.resolve_all_input_files(args),
                                 args.output_file, args.output_dir))
    exp_result: ExpResult = runner.run()

    for result in exp_result:
        print(result)


if __name__ == "__main__":
    main()

