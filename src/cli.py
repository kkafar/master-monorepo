import argparse
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import os


@dataclass
class Args:
    bin: Path
    file: Optional[Path]
    dir: Optional[Path]


def validate_cli_args(args: Args):
    assert args.bin is not None, "Path to binary of jssp instance solver must be specified"
    assert args.bin.is_file(), "Provided binary path must point to an existing file"
    assert os.access(args.bin, os.X_OK), "Provided binary file must have executable permission granted"
    
    if args.file is not None:
        assert args.file.is_file(), "Provided data file path must point to an existing file"
        assert os.access(args.file, os.R_OK), "Data file must have read permission granted"

    if args.dir is not None:
        assert args.dir.is_dir(), "Provided data directory path must point to an existing directory"
        assert os.access(args.file, os.R_OK), "Data directory must have read permission granted"


def build_cli() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ECDataKitRunner",
        description="Simple CLI tool to orchestrate ECRS JSSP experiments",
        epilog="""
            Please note that --file & --dir options are mutually exclusive.
            Authored by Kacper Kafara <kacperkafara@gmail.com>.
            """
    )
    parser.add_argument('bin', help='path to jssp instance solver')
    mutex_group = parser.add_mutually_exclusive_group()
    mutex_group.add_argument('-f', '--file', help='path to jssp instance data file', type=Path)
    mutex_group.add_argument('-d', '--dir', help='path to jssp instance data directory', type=Path)
    return parser


def parse_cli_args() -> Args:
    args: Args = build_cli().parse_args()
    validate_cli_args(args)
    return args
