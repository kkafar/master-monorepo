import argparse
from pathlib import Path
from .args import Args
from .command import (
    handle_cmd_run,
    handle_cmd_analyze,
    handle_cmd_perfcmp,
    handle_cmd_compare,
    handle_cmd_validate_instance_spec
)
from .validation import validate_cli_args


def build_run_parser(subparsers: argparse._SubParsersAction) -> None:
    run_parser = subparsers.add_parser(name="run", help="Run experiment(s) & analyze the results")
    run_parser.add_argument('bin', help='Path to jssp instance solver', type=Path)
    run_parser.add_argument('-i', '--input-files', required=True, help='Path to jssp instance data file/directory or list of those', nargs='+', type=Path)
    run_parser.add_argument('-o', '--output-dir', help='Parent directory experiment batch output directory will be placed in; should be specified in case multiple input files / directory/ies were specified', type=Path)
    run_parser.add_argument('-c', '--solver-config', help='Solver configuration file', type=Path, dest='config_file')
    run_parser.add_argument('-n', '--n-series', help='Number of repetitions for each problem instance. Defaults to 1.', type=int, dest='runs')
    run_parser.add_argument('-m', '--metadata-file', type=Path, help='Path to file with instance metadata', dest='metadata_file')
    run_parser.add_argument('-p', '--procs', type=int, help='Number of processes to run in parallel; works only on local configuration', default=1)
    run_parser.add_argument('--attach-timestamp', action=argparse.BooleanOptionalAction, type=bool,
                            help='Whether a timestamp should be attached to output file name', default=True, dest='attach_timestamp')
    run_parser.add_argument('--hq', action=argparse.BooleanOptionalAction, type=bool, default=False, dest='hq', help='Whether HyperQueue should be used')
    run_parser.add_argument('--ex-postprocess', action=argparse.BooleanOptionalAction, type=bool, default=False, help='Experimental. Whether to run postprocessing tasks after finalizing computations', dest='experimental_postprocess')
    run_parser.set_defaults(handler=handle_cmd_run)


def build_analyze_parser(subparsers: argparse._SubParsersAction) -> None:
    analyze_parser = subparsers.add_parser(name="analyze", help="Analyze experiment(s) result(s)")
    analyze_parser.add_argument('-i', '--input-dir', help='Directory with the result files', type=Path, required=True)
    analyze_parser.add_argument('-m', '--metadata-file', type=Path, required=False, help='Path to file with instance metadata', dest='metadata_file')
    analyze_parser.add_argument('-o', '--output-dir', type=Path, required=False, help='Ouput directory for analysis result. If not specified, no results are saved')
    analyze_parser.add_argument('-p', '--procs', type=int, required=False, help='Number of processes to run in parallel', default=1)
    analyze_parser.add_argument('--plot', type=bool, action=argparse.BooleanOptionalAction, required=False, default=True, dest='plot', help='Whether the plots should be created')
    analyze_parser.set_defaults(handler=handle_cmd_analyze)


def build_pefcmp_parser(subparsers: argparse._SubParsersAction) -> None:
    perfcmp_parser = subparsers.add_parser(name="perfcmp", help="Compare performance information of two experiments: bench against base")
    perfcmp_parser.add_argument('basepath', type=Path, help='Path to directory with processed data of baseline experiment batch. The CMPPATH will be compared relatively to it.')
    perfcmp_parser.add_argument('benchpath', type=Path, help='Path to directory with processed data of experiment batch to be compared against BASEPATH')
    perfcmp_parser.set_defaults(handler=handle_cmd_perfcmp)


def build_compare_parser(subparsers: argparse._SubParsersAction) -> None:
    compare_parser = subparsers.add_parser(name='compare', help='Compare statistics for given list of experiments; table for each pair will be generated')
    compare_parser.add_argument('-d', '--exp-dirs', type=Path, nargs='+', required=True, help='Directories with PROCESSED experiments data; directory for each exp to compare')
    compare_parser.add_argument('-o', '--output-dir', type=Path, required=False, help='Output directory to save the results to')
    compare_parser.set_defaults(handler=handle_cmd_compare)


def build_validate_instance_file_parser(subparsers: argparse._SubParsersAction) -> None:
    validate_parser = subparsers.add_parser(name='validate-instance-spec', help='Validate structure of input file')
    validate_parser.add_argument('-i', '--input-files', required=True,
                                 help='Path to jssp instance data file/directory or list of those',
                                 nargs='+', type=Path)
    validate_parser.set_defaults(handler=handle_cmd_validate_instance_spec)


def build_cli() -> argparse.ArgumentParser:
    main_parser = argparse.ArgumentParser(
        prog="ECDataKitRunner",
        description="Simple CLI tool to orchestrate ECRS JSSP experiments",
        epilog="""
            Authored by Kacper Kafara <kacperkafara@gmail.com>.
            """
    )

    subparsers = main_parser.add_subparsers(
        title="Commands",
        description="Specify the command to execute",
        dest='cmd_name',
        required=True
    )

    build_run_parser(subparsers)
    build_analyze_parser(subparsers)
    build_compare_parser(subparsers)
    build_pefcmp_parser(subparsers)
    build_validate_instance_file_parser(subparsers)

    return main_parser


def parse_cli_args() -> Args:
    args: Args = build_cli().parse_args()

    validate_cli_args(args)
    return args
