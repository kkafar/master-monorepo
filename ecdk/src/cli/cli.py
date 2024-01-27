import argparse
from pathlib import Path
import os
from .args import Args, RunCmdArgs, AnalyzeCmdArgs, PerfcmpCmdArgs, CompareCmdArgs
from .command import (
    handle_cmd_run,
    handle_cmd_analyze,
    handle_cmd_perfcmp,
    handle_cmd_compare
)


def validate_base_args(args: Args):
    assert args.cmd_name in ['run', 'analyze', 'perfcmp', 'compare'], "Unrecognized command name"


def validate_run_cmd_args(args: RunCmdArgs):
    assert args.bin is not None, "Path to binary of jssp instance solver must be specified"
    assert args.bin.is_file(), "Provided binary path must point to an existing file"
    assert os.access(args.bin, os.X_OK), "Provided binary file must have executable permission granted"

    assert args.input_files is not None, "At least one input file / directory must be specified"

    if args.input_files is not None:
        for file in args.input_files:
            assert file.is_file() or file.is_dir(), f'{file} is neither a file nor a directory'
            assert os.access(file, os.R_OK), f'{file} does not have read permissions'

    if args.output_dir is not None and not args.output_dir.is_dir():
        # Hey, nice sideeffects in validation code...
        # TODO: REMOVE IT FROM HERE
        args.output_dir.mkdir(parents=True, exist_ok=True)
        assert args.output_dir.is_dir(), "Output directory was specified but it does not exist and couldn't be created"

    if args.metadata_file is not None:
        assert args.metadata_file.is_file(), f"Metadata file {args.metadata_file} is not a file"

    if args.procs is not None:
        assert args.procs >= 1, f"Number of processes must be >= 1 but received {args.procs}"

    if args.config_file is not None:
        assert args.config_file.is_file(), "Specified config file must exist"


def validate_analyze_cmd_args(args: AnalyzeCmdArgs):
    assert args.dir.is_dir(), f'{args.dir} is not a directory'
    if args.procs is not None:
        assert args.procs > 0, f'Number of processes must be > 0. Received {args.procs}'
    # Output directory (if specified) will be initialized in command handler
    # if args.output_dir is not None:
    #     assert args.output_dir.is_dir(), "Output directory was specified but it does not exist and couldn't be created"


def validate_perfcmp_cmd_args(args: PerfcmpCmdArgs):
    assert args.basepath.is_dir()
    assert args.benchpath.is_dir()


def validate_compare_cmd_args(args: CompareCmdArgs):
    assert len(args.exp_dirs) > 1
    if args.output_dir is not None:
        assert args.output_dir.is_dir()


def validate_cli_args(args: Args):
    validate_base_args(args)
    match args.cmd_name:
        case 'run':
            validate_run_cmd_args(args)
        case 'analyze':
            validate_analyze_cmd_args(args)
        case 'perfcmp':
            validate_perfcmp_cmd_args(args)
        case 'compare':
            validate_compare_cmd_args(args)
        case _:
            assert False, "Unrecognized command type"


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
    run_parser.add_argument('-o', '--output-dir', help='Output directory; should be specified in case multiple input files / directory/ies were specified', type=Path)
    run_parser.add_argument('--config-file', help='Solver configuration file', type=Path, required=False)
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


def parse_cli_args() -> Args:
    args: Args = build_cli().parse_args()
    validate_cli_args(args)
    return args
