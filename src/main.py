#!/usr/bin/env python3
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --partition=plgrid
#SBATCH --time=24:00:00
#SBATCH --account=plglscclass23-cpu
#SBATCH --cpus-per-task=36
#SBATCH --mem-per-cpu=512M

import sys
from pathlib import Path
print(f"cwd/src: {Path.cwd().joinpath('src')}")
sys.path.append(str(Path.cwd().joinpath('src')))

import polars as pl
import matplotlib.pyplot as plt
import cli.cli as cli


def configure_env():
    pl.Config.set_tbl_rows(20)
    pl.Config.set_tbl_cols(10)
    plt.rcParams['figure.figsize'] = (16, 9)


def main():
    configure_env()
    args = cli.parse_cli_args()
    args.handler(args)


if __name__ == "__main__":
    main()

