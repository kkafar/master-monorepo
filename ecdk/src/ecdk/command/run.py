from core.env import EnvContext
from cli.args import RunCmdArgs

from experiment.runner import LocalExperimentBatchRunner, HyperQueueRunner
from experiment.solver import SolverProxy
from experiment.model import (
    ExperimentConfig,
    Experiment
)
from data.file_resolver import resolve_all_input_files
from data.tools import (
    maybe_load_instance_metadata,
)
from core.tools import (
    exp_name_from_input_file,
    output_dir_for_experiment_with_name,
    attach_timestamp_to_dir,
    current_timestamp
)
from core.fs import initialize_file_hierarchy


def run(ctx: EnvContext, args: RunCmdArgs):
    metadata_store = maybe_load_instance_metadata(args.metadata_file)

    # Not recursive as we don't want to load Taillard specification
    input_files = resolve_all_input_files(args.input_files, recursive=False)
    batch = []

    base_dir = args.output_dir
    if not ctx.is_ares and args.attach_timestamp:
        base_dir = attach_timestamp_to_dir(base_dir, current_timestamp())

    for file in input_files:
        name = exp_name_from_input_file(file)
        metadata = metadata_store.get(name)
        if metadata is None:
            print(f"Missing metadata for {metadata}")
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

    experiment_configs = [exp.config for exp in batch]
    solver = SolverProxy(args.bin)

    if args.hq and ctx.is_ares:
        HyperQueueRunner(solver).run(experiment_configs)
    else:
        LocalExperimentBatchRunner(
            solver,
            experiment_configs
        ).run(process_limit=args.procs)

