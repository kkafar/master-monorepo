from cli.args import PerfcmpCmdArgs
from data.processing import compare_exp_batch_outputs
from context import Context


def perfcmp(ctx: Context, args: PerfcmpCmdArgs):
    compare_exp_batch_outputs(args.basepath, args.benchpath)
