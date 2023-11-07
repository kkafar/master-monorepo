from .args import RunCmdArgs, AnalyzeCmdArgs, PerfcmpCmdArgs
from experiment.runner import LocalExperimentBatchRunner, AresExpScheduler
from experiment.solver import SolverProxy
from experiment.model import (
    ExperimentResult,
    ExperimentConfig,
    Experiment
)
from data.file_resolver import resolve_all_input_files
from data.processing import process_experiment_batch_output, compare_exp_batch_outputs
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
from core.env import is_running_on_ares


def handle_cmd_run(args: RunCmdArgs):
    print(f"RunCommand run with args: {args}")
    metadata_store = maybe_load_instance_metadata(args.metadata_file)

    # Not recursive as we don't want to load Taillard specification
    input_files = resolve_all_input_files(args.input_files, recursive=False)
    batch = []

    base_dir = args.output_dir
    if not is_running_on_ares() and args.attach_timestamp:
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
                config=ExperimentConfig(file,
                                        out_dir,
                                        args.config_file,
                                        args.runs if args.runs else 1),
                result=None
            )
        )

    # Create file hierarchy & dump configuration data
    initialize_file_hierarchy(batch)

    LocalExperimentBatchRunner(
        SolverProxy(args.bin),
        [exp.config for exp in batch]
    ).run(process_limit=args.procs)


def handle_cmd_analyze(args: AnalyzeCmdArgs):
    print(f"AnalyzeCommand run with args: {args}")

    experiment_batch: list[Experiment] = extract_experiments_from_dir(args.dir)

    if args.output_dir is not None:
        init_processed_data_file_hierarchy(experiment_batch, args.output_dir)

    process_experiment_batch_output(experiment_batch, args.output_dir)


def handle_cmd_perfcmp(args: PerfcmpCmdArgs):
    print(f"PerfcmpCommand run with args: {args}")
    compare_exp_batch_outputs(args.basepath, args.benchpath)

