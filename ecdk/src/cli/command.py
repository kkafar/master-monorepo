from .args import RunCmdArgs, AnalyzeCmdArgs, PerfcmpCmdArgs
from context import Context


def handle_cmd_run(ctx: Context, args: RunCmdArgs):
    print(f"RunCommand run with args: {args}, ctx: {ctx}")
    from command import run
    run(ctx, args)


def handle_cmd_analyze(ctx: Context, args: AnalyzeCmdArgs):
    print(f"AnalyzeCommand run with args: {args}")
    from command import analyze
    analyze(ctx, args)


def handle_cmd_perfcmp(ctx: Context, args: PerfcmpCmdArgs):
    print(f"PerfcmpCommand run with args: {args}")
    from command import perfcmp
    perfcmp(ctx, args)

