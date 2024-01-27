import argparse
from pathlib import Path
from .args import Args
from .command import (
    handle_cmd_run,
    handle_cmd_analyze,
    handle_cmd_perfcmp,
    handle_cmd_compare
)
from .validation import validate_cli_args
from core.env import EnvContext


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

    run_parser = subparsers.add_parser(name="run", help="Run experiment(s) & analyze the results")
    run_parser.add_argument('bin', help='Path to jssp instance solver', type=Path)
    run_parser.add_argument('-i', '--input-files', help='Path to jssp instance data file/directory or list of those', nargs='+', type=Path)
    run_parser.add_argument('-o', '--output-dir', help='Output directory experiment batch result will be placed in; should be specified in case multiple input files / directory/ies were specified', type=Path)
    run_parser.add_argument('-c', '--solver-config', help='Solver configuration file', type=Path, required=False, dest='config_file')
    run_parser.add_argument('-n', '--runs', help='Number of repetitions for each problem instance. Defaults to 1.', type=int)
    run_parser.add_argument('-m', '--metadata-file', type=Path, required=True, help='Path to file with instance metadata', dest='metadata_file')
    run_parser.add_argument('-p', '--procs', type=int, required=False, help='Number of processes to run in parallel', default=1)
    run_parser.add_argument('--attach-timestamp', action=argparse.BooleanOptionalAction, type=bool,
                            required=False, help='Whether a timestamp should be attached to output file name', default=True, dest='attach_timestamp')
    run_parser.add_argument('--hq', action=argparse.BooleanOptionalAction, type=bool, required=False, default=False, dest='hq', help='Whether HyperQueue should be used')
    run_parser.set_defaults(handler=handle_cmd_run)

    analyze_parser = subparsers.add_parser(name="analyze", help="Analyze experiment(s) result(s)")
    analyze_parser.add_argument('-i', '--dir', help='Directory with the result files', type=Path, required=True)
    analyze_parser.add_argument('-m', '--metadata-file', type=Path, required=True, help='Path to file with instance metadata', dest='metadata_file')
    analyze_parser.add_argument('-o', '--output-dir', type=Path, required=False, help='Ouput directory for analysis result. If not specified, no results are saved')
    analyze_parser.add_argument('-p', '--procs', type=int, required=False, help='Number of processes to run in parallel', default=1)
    analyze_parser.add_argument('--plot', type=bool, action=argparse.BooleanOptionalAction, required=False, default=True, dest='plot', help='Whether the plots should be created')
    analyze_parser.set_defaults(handler=handle_cmd_analyze)

    perfcmp_parser = subparsers.add_parser(name="perfcmp", help="Compare performance information of two experiments: bench against base")
    perfcmp_parser.add_argument('basepath', type=Path, help='Path to directory with processed data of baseline experiment batch. The CMPPATH will be compared relatively to it.')
    perfcmp_parser.add_argument('benchpath', type=Path, help='Path to directory with processed data of experiment batch to be compared against BASEPATH')
    perfcmp_parser.set_defaults(handler=handle_cmd_perfcmp)

    compare_parser = subparsers.add_parser(name='compare', help='Compare statistics for given list of experiments; table for each pair will be generated')
    compare_parser.add_argument('-d', '--exp-dirs', type=Path, nargs='+', required=True, help='Directories with PROCESSED experiments data; directory for each exp to compare')
    compare_parser.add_argument('-o', '--output-dir', type=Path, required=False, help='Output directory to save the results to')
    compare_parser.set_defaults(handler=handle_cmd_compare)

    return main_parser


def parse_cli_args(ctx: EnvContext) -> Args:
    args: Args = build_cli().parse_args()

    validate_cli_args(args)
    return args
