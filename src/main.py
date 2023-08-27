import polars as pl
import matplotlib.pyplot as plt
import cli
import data.file_resolver as fr
from experiment.config import ExperimentBatchDesc
from experiment.runner import ExperimentBatchRunner, ExperimentResult
from experiment.solver import SolverProxy
from data.tools import process_experiment_results


def configure_env():
    pl.Config.set_tbl_rows(20)
    pl.Config.set_tbl_cols(10)
    plt.rcParams['figure.figsize'] = (16, 9)


def main():
    configure_env()
    args = cli.parse_cli_args()
    runner = ExperimentBatchRunner(
        SolverProxy(args.bin),
        ExperimentBatchDesc(fr.resolve_all_input_files(args),
                            args.output_file, args.output_dir,
                            repeats_no=args.runs if args.runs is not None else 1))
    exp_results: list[ExperimentResult] = runner.run()

    # for result in exp_results:
    #     print(result)

    process_experiment_results(exp_results)


if __name__ == "__main__":
    main()

