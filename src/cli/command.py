from .args import RunCmdArgs, AnalyzeCmdArgs
from experiment.runner import ExperimentBatchRunner
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
from core.tools import (
    exp_name_from_input_file,
    output_dir_for_experiment_with_name,
    attach_timestamp_to_dir,
    current_timestamp
)
from core.series import (
    materialize_all_series_outputs
)



def handle_cmd_run(args: RunCmdArgs):
    print(f"RunCommand run with args: {args}")
    metadata_store = maybe_load_instance_metadata(args.metadata_file)

    input_files = resolve_all_input_files(args.input_files, recursive=False)
    batch = []

    base_dir = args.output_dir
    if args.attach_timestamp:
        base_dir = attach_timestamp_to_dir(base_dir, current_timestamp())

    for file in input_files:
        name = exp_name_from_input_file(file)
        metadata = metadata_store.get(name)
        print(f"Looking up metadata for {name}: {metadata}")
        out_dir = output_dir_for_experiment_with_name(name, base_dir)
        batch.append(
            Experiment(
                name=name,
                instance=metadata,  # WARN: This may fail for few experiments
                run_config=ExperimentConfig(file,
                                            out_dir,
                                            args.runs if args.runs else 1),
                run_result=None
            )
        )

    results: list[ExperimentResult] = ExperimentBatchRunner(
        SolverProxy(args.bin),
        [exp.run_config for exp in batch]
    ).run(process_limit=args.procs)

    for exp_result in results:
        materialize_all_series_outputs(exp_result.series_outputs, force=False)
    exit(0)

    for (exp, result) in zip(batch, results):
        exp.run_result = result

    process_experiment_batch_output(batch)


def handle_cmd_analyze(args: AnalyzeCmdArgs):
    print(f"AnalyzeCommand run with args: {args}")

    exp_results: list[ExperimentResult] = extract_experiment_results_from_dir(args.dir)
    process_experiment_batch_output(exp_results)

