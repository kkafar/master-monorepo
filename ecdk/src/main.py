#!/usr/bin/env python3
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --partition=plgrid
#SBATCH --time=24:00:00
#SBATCH --account=plglscclass23-cpu
#SBATCH --cpus-per-task=36
#SBATCH --mem-per-cpu=512M
#SBATCH --mail-type=begin
#SBATCH --mail-type=end
#SBATCH --mail-user=kkafara@student.agh.edu.pl

import sys
from pathlib import Path
print(f"cwd/src: {Path.cwd().joinpath('src')}")
sys.path.append(str(Path.cwd().joinpath('src')))

import polars as pl
import matplotlib.pyplot as plt
import cli
from core.env import EnvContext


def configure_env():
    pl.Config.set_tbl_rows(50)
    pl.Config.set_tbl_cols(20)
    pl.Config.set_fmt_float('mixed')
    pl.Config.set_float_precision(2)
    plt.rcParams['figure.figsize'] = (16, 9)


def main():
    configure_env()
    ctx = EnvContext(strict=True)
    args = cli.parse_cli_args(ctx)  # TODO: This should be other way around. Context should be create basing on args and then validated
    args.handler(ctx, args)


if __name__ == "__main__":
    main()

