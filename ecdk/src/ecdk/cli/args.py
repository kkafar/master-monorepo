from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Callable
from context import Context


@dataclass
class Args:
    cmd_name: str
    handler: Callable[[Context, 'Args'], None]


@dataclass
class RunCmdArgs(Args):
    bin: Path
    input_files: Optional[list[Path]]
    output_dir: Optional[Path]
    config_file: Optional[Path]
    runs: Optional[int]
    metadata_file: Optional[Path]
    procs: Optional[int]
    attach_timestamp: bool
    hq: bool
    experimental_postprocess: bool


@dataclass
class AnalyzeCmdArgs(Args):
    input_dir: Path
    metadata_file: Path
    output_dir: Optional[Path]
    procs: Optional[int]
    plot: bool


@dataclass
class PerfcmpCmdArgs(Args):
    basepath: Path
    benchpath: Path


@dataclass
class CompareCmdArgs(Args):
    exp_dirs: list[Path]
    output_dir: Optional[Path]


@dataclass
class ValidateInstanceSpecArgs(Args):
    input_files: Optional[list[Path]]

