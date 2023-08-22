import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class Args:
    bin: Path
    input_file: Path
    output_file: Path
    input_dir: Optional[Path]
    output_dir: Optional[Path]


def validate_cli_args(args: Args):
    assert args.bin is not None, "Path to binary of jssp instance solver must be specified"
    assert args.bin.is_file(), "Provided binary path must point to an existing file"
    assert os.access(args.bin, os.X_OK), "Provided binary file must have executable permission granted"

    if args.input_file is not None:
        assert args.input_file.is_file(), "Provided input data file path must point to an existing file"
        assert os.access(args.input_file, os.R_OK), "Data input file must have read permission granted"

    if args.input_dir is not None:
        assert args.input_dir.is_dir(), "Provided data directory path must point to an existing directory"
        assert os.access(args.input_dir, os.R_OK), "Data directory must have read permission granted"

    if args.output_file is not None and args.output_dir is not None:
        parts = args.output_file.parts
        assert len(parts) == 1 or len(parts) == 2 and parts[0] == '.', "If output dir is specified output file should specify base pattern for output files"


def build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ECDataKitRunner",
        description="Simple CLI tool to orchestrate ECRS JSSP experiments",
        epilog="""
            Authored by Kacper Kafara <kacperkafara@gmail.com>.
            """
    )
    parser.add_argument('bin', help='path to jssp instance solver', type=Path)
    # mutex_group = parser.add_mutually_exclusive_group()
    parser.add_argument('-f', '--input-file', help='path to jssp instance data file', type=Path)
    parser.add_argument('-o', '--output-file', help='output file path', type=Path)
    parser.add_argument('-d', '--input-dir', help='path to jssp instance data directory', type=Path)
    parser.add_argument('-D', '--output-dir', help='output directory', type=Path)
    return parser


def parse_cli_args() -> Args:
    args: Args = build_cli().parse_args()
    validate_cli_args(args)
    return args
