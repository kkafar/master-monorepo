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

