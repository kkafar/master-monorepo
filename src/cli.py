import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class Args:
    bin: Path
    input_files: Optional[list[Path]]
    input_dirs: Optional[list[Path]]
    output_file: Optional[Path]
    output_dir: Optional[Path]
    runs: Optional[int]


def validate_cli_args(args: Args):
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


def build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ECDataKitRunner",
        description="Simple CLI tool to orchestrate ECRS JSSP experiments",
        epilog="""
            Authored by Kacper Kafara <kacperkafara@gmail.com>.
            """
    )
    parser.add_argument('bin', help='Path to jssp instance solver', type=Path)
    # mutex_group = parser.add_mutually_exclusive_group()
    parser.add_argument('-f', '--input-files', help='Path to jssp instance data file or list of those', nargs='+', type=Path)
    parser.add_argument('-d', '--input-dirs', help='Path to jssp instance data directory or list of those', nargs='+', type=Path)
    parser.add_argument('-o', '--output-file', help='Output file path; should be used only when in case single input file was specified', type=Path)
    parser.add_argument('-D', '--output-dir', help='Output directory; should be specified in case multiple input files / directory/ies were specified', type=Path)
    parser.add_argument('--runs', help='Number of repetitions for each problem instance. Defaults to 1.', type=int)
    return parser


def parse_cli_args() -> Args:
    args: Args = build_cli().parse_args()
    validate_cli_args(args)
    return args
