from .args import RunCmdArgs, AnalyzeCmdArgs, PerfcmpCmdArgs, CompareCmdArgs, ValidateInstanceSpecArgs
from context import Context


def handle_cmd_run(ctx: Context, args: RunCmdArgs):
    print(f"RunCommand run with args: {args}")
    from command.run import run
    run(ctx, args)


def handle_cmd_analyze(ctx: Context, args: AnalyzeCmdArgs):
    print(f"AnalyzeCommand run with args: {args}")
    from command.analyze import analyze
    analyze(ctx, args)


def handle_cmd_perfcmp(ctx: Context, args: PerfcmpCmdArgs):
    print(f"PerfcmpCommand run with args: {args}")
    from command.perfcmp import perfcmp
    perfcmp(ctx, args)


def handle_cmd_compare(ctx: Context, args: CompareCmdArgs):
    print(f"CompareCmmand run with args: {args}")
    from command.compare import compare
    compare(ctx, args)


def handle_cmd_validate_instance_spec(ctx: Context, args: ValidateInstanceSpecArgs):
    print(f"ValidateInstanceSpecCommand running with args: {args}")
    from command.validate import validate_instance_spec
    validate_instance_spec(ctx, args)

