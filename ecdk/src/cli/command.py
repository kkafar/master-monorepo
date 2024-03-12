from .args import RunCmdArgs, AnalyzeCmdArgs, PerfcmpCmdArgs
from context import Context
from command import run, analyze, perfcmp


def handle_cmd_run(ctx: Context, args: RunCmdArgs):
    print(f"RunCommand run with args: {args}, ctx: {ctx}")
    run(ctx, args)


def handle_cmd_analyze(ctx: Context, args: AnalyzeCmdArgs):
    print(f"AnalyzeCommand run with args: {args}")
    analyze(ctx, args)


def handle_cmd_perfcmp(ctx: Context, args: PerfcmpCmdArgs):
    print(f"PerfcmpCommand run with args: {args}")
    perfcmp(ctx, args)

