import os
from .args import (
    Args,
    RunCmdArgs,
    AnalyzeCmdArgs,
    PerfcmpCmdArgs,
    CompareCmdArgs
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
