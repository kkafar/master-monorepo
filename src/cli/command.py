import core
import itertools as it
from .args import RunCmdArgs, AnalyzeCmdArgs
from experiment.runner import ExperimentBatchRunner, ExperimentBatchConfig
from experiment.solver import SolverProxy
from experiment.model import (
    ExperimentResult,
    ExperimentConfig,
    Experiment
)
from data.file_resolver import resolve_all_input_files
from data.tools import (
    process_experiment_batch_output,
    extract_experiment_results_from_dir,
    maybe_load_instance_metadata
)


def handle_cmd_run(args: RunCmdArgs):
    print(f"RunCommand run with args: {args}")
    metadata_store = maybe_load_instance_metadata(args.metadata_file)

    input_files = resolve_all_input_files(args.input_files, args.input_dirs)
    batch = []
    for file in input_files:
        name = core.tools.exp_name_from_input_file(file)
        batch.append(
            Experiment(
                name=name,
                instance=metadata_store.get(name), # WARN: This may fail for few experiments
                run_config=ExperimentConfig(file, args.output_dir, args.runs if args.runs else 1),
                run_result=None
            )
        )

    results: list[ExperimentResult] = ExperimentBatchRunner(
        SolverProxy(args.bin),
        [exp.run_config for exp in batch]
    ).run()

    for (exp, result) in zip(batch, results):
        exp.run_result = result


    process_experiment_batch_output(batch)


def handle_cmd_analyze(args: AnalyzeCmdArgs):
    print(f"AnalyzeCommand run with args: {args}")

    exp_results: list[ExperimentResult] = extract_experiment_results_from_dir(args.dir)
    process_experiment_batch_output(exp_results)

