from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Callable
from core.env import EnvContext


@dataclass
class Args:
    cmd_name: str
    handler: Callable[[EnvContext, 'Args'], None]


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


@dataclass
class AnalyzeCmdArgs(Args):
    dir: Path
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
