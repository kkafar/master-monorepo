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

    assert args.input_files is not None or args.input_dirs is not None, "One of input files or input dirs must be specified"

    if args.input_files is not None:
        for file in args.input_files:
            assert file.is_file(), f'{file} is not a file'
            assert os.access(file, os.R_OK), f'{file} does not have read permissions'

    if args.input_dirs is not None:
        for input_dir in args.input_dirs:
            assert input_dir.is_dir(), f'{input_dir} is not a directory'
            assert os.access(input_dir, os.R_OK), f'{input_dir} does not have read permission granted'

    if args.output_file is not None:
        assert args.input_files is not None and len(args.input_files) == 1, "For output_file option to work exactly one input file must be specified"

    if args.output_dir is not None and not args.output_dir.is_dir():
        args.output_dir.mkdir(parents=True)
        assert args.output_dir.is_dir(), "Output directory was specified but it does not exist and couldn't be created"

    if args.metadata_file is not None:
        assert args.metadata_file.is_file(), f"Metadata file {args.metadata_file} is not a file"


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
    run_parser.add_argument('-f', '--input-files', help='Path to jssp instance data file or list of those', nargs='+', type=Path)
    run_parser.add_argument('-d', '--input-dirs', help='Path to jssp instance data directory or list of those', nargs='+', type=Path)
    run_parser.add_argument('-o', '--output-file', help='Output file path; should be used only when in case single input file was specified', type=Path)
    run_parser.add_argument('-D', '--output-dir', help='Output directory; should be specified in case multiple input files / directory/ies were specified', type=Path)
    run_parser.add_argument('--runs', help='Number of repetitions for each problem instance. Defaults to 1.', type=int)
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
