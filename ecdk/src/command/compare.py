from core.env import EnvContext
from cli.args import PerfcmpCmdArgs
from data.processing import compare_processed_exps


def compare(ctx: EnvContext, args: PerfcmpCmdArgs):
    compare_processed_exps(args.exp_dirs, args.output_dir)

