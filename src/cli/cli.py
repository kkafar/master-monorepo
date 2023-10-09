import argparse
from pathlib import Path
import os
from .args import Args, RunCmdArgs, AnalyzeCmdArgs
from .command import (
    handle_cmd_run,
    handle_cmd_analyze,
)


def validate_base_args(args: Args):
    assert args.cmd_name in ['run', 'analyze'], "Unrecognized command name"


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
        args.output_dir.mkdir(parents=True)
        assert args.output_dir.is_dir(), "Output directory was specified but it does not exist and couldn't be created"

    if args.metadata_file is not None:
        assert args.metadata_file.is_file(), f"Metadata file {args.metadata_file} is not a file"

    if args.procs is not None:
        assert args.procs >= 1, f"Number of processes must be >= 1 but received {args.procs}"


def validate_analyze_cmd_args(args: AnalyzeCmdArgs):
    assert args.dir.is_dir(), f'{args.dir} is not a directory'


def validate_cli_args(args: Args):
    global CMD_RUN
    global CMD_ANALYZE
    validate_base_args(args)
    match args.cmd_name:
        case 'run':
            validate_run_cmd_args(args)
        case 'analyze':
            validate_analyze_cmd_args(args)
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
    run_parser.add_argument('-n', '--runs', help='Number of repetitions for each problem instance. Defaults to 1.', type=int)
    run_parser.add_argument('-m', '--metadata-file', type=Path, required=False, help='Path to file with instance metadata information', dest='metadata_file')
    run_parser.add_argument('-p', '--procs', type=int, required=False, help='Number of processes to run in parallel', default=1)
    run_parser.set_defaults(handler=handle_cmd_run)

    analyze_parser = subparsers.add_parser(name="analyze", help="Analyze experiment(s) result(s)")
    # analyze_parser.add_argument('--names', help='Experiment names to analyze. Note that output files must have default names.', nargs='+', type=str, required=True)
    analyze_parser.add_argument('--dir', help='Directory with the result files', type=Path, required=True)
    # group = analyze_parser.add_mutually_exclusive_group(required=True)
    # group.add_argument('--names', help='Experiment names to analyze. Note that output files must have default names.', nargs='+', type=str)
    analyze_parser.set_defaults(handler=handle_cmd_analyze)
    # group.add_argument('--

    return main_parser


def parse_cli_args() -> Args:
    args: Args = build_cli().parse_args()
    validate_cli_args(args)
    return args
