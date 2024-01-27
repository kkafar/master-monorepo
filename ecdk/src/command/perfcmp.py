from core.env import EnvContext
from cli.args import PerfcmpCmdArgs
from data.processing import compare_exp_batch_outputs


def perfcmp(ect: EnvContext, args: PerfcmpCmdArgs):
    compare_exp_batch_outputs(args.basepath, args.benchpath)
