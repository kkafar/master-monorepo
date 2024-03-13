from cli.args import PerfcmpCmdArgs
from data.processing import compare_processed_exps
from context import Context


def compare(ctx: Context, args: PerfcmpCmdArgs):
    compare_processed_exps(args.exp_dirs, args.output_dir)

