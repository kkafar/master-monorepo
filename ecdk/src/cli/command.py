from .args import RunCmdArgs, AnalyzeCmdArgs, PerfcmpCmdArgs, CompareCmdArgs
from experiment.runner import LocalExperimentBatchRunner, AresExpScheduler, HyperQueueRunner
from experiment.solver import SolverProxy
from experiment.model import (
    ExperimentResult,
    ExperimentConfig,
    Experiment
)
from data.file_resolver import resolve_all_input_files
from data.processing import (
    process_experiment_batch_output,
    compare_exp_batch_outputs,
    compare_processed_exps
)
from data.tools import (
    maybe_load_instance_metadata,
    extract_experiments_from_dir,
)
from core.tools import (
    exp_name_from_input_file,
    output_dir_for_experiment_with_name,
    attach_timestamp_to_dir,
    current_timestamp
)
from core.fs import initialize_file_hierarchy, init_processed_data_file_hierarchy
from core.env import EnvContext


def handle_cmd_run(ctx: EnvContext, args: RunCmdArgs):
    print(f"RunCommand run with args: {args}")
    from command.run import run
    run(ctx, args)


def handle_cmd_analyze(ctx: EnvContext, args: AnalyzeCmdArgs):
    print(f"AnalyzeCommand run with args: {args}")
    from command.analyze import analyze
    analyze(ctx, args)


def handle_cmd_perfcmp(ctx: EnvContext, args: PerfcmpCmdArgs):
    print(f"PerfcmpCommand run with args: {args}")
    from command.perfcmp import perfcmp
    perfcmp(ctx, args)


def handle_cmd_compare(args: CompareCmdArgs):
    print(f"CompareCmmand run with args: {args}")
    compare_processed_exps(args.exp_dirs, args.output_dir)
