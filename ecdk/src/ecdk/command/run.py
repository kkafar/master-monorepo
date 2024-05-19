from cli.args import RunCmdArgs
from experiment.runner import LocalExperimentBatchRunner, HyperQueueRunner
from experiment.solver import SolverProxy
from experiment.model import (
    ExperimentConfig,
    Experiment,
    ExperimentBatch,
    SolverConfigFile,
    SolverExecutableInfo,
    EcdkInfo,
)
from data.file_resolver import resolve_all_input_files
from data.tools import maybe_load_instance_metadata
from core.tools import (
    exp_name_from_input_file,
    output_dir_for_experiment_with_name,
    attach_timestamp_to_dir,
    current_timestamp_iso8601
)
from core.fs import initialize_file_hierarchy
from core.version import Version
from context import Context


def run(ctx: Context, args: RunCmdArgs):
    metadata_store = maybe_load_instance_metadata(args.metadata_file or ctx.instance_metadata_file)

    # Not recursive as we don't want to load Taillard specification
    input_files = resolve_all_input_files(args.input_files, recursive=False)

    base_dir = args.output_dir

    start_timestamp = current_timestamp_iso8601()

    if not ctx.is_ares and args.attach_timestamp:
        base_dir = attach_timestamp_to_dir(base_dir, start_timestamp)

    batch = []
    for file in input_files:
        name = exp_name_from_input_file(file)
        metadata = metadata_store.get(name)
        assert metadata is not None, f"Missing metadata for {metadata}. Aborting."
        out_dir = output_dir_for_experiment_with_name(name, base_dir)
        batch.append(
            Experiment(
                name=name,
                instance=metadata,  # WARN: This may fail for few experiments
                config=ExperimentConfig(file,
                                        out_dir,
                                        args.config_file,
                                        args.runs if args.runs else 1),
                result=None,
                batch_dir=base_dir
            )
        )

    solver_proxy = SolverProxy(args.bin)
    solver_config = SolverConfigFile(args.config_file) if args.config_file else None
    solver_info = SolverExecutableInfo(version=solver_proxy.version())
    ecdk_info = EcdkInfo(version=ctx.ecdk_version)

    batch = ExperimentBatch(output_dir=base_dir,
                            experiments=batch,
                            solver_config=solver_config,
                            start_time=start_timestamp,
                            solver_info=solver_info,
                            ecdk_info=ecdk_info)

    # Create file hierarchy & dump configuration data
    initialize_file_hierarchy(batch)

    experiment_configs = [exp.config for exp in batch.experiments]

    if args.hq and ctx.is_ares:
        HyperQueueRunner(solver_proxy).run(batch, ctx=ctx, postprocess=args.experimental_postprocess)
    else:
        LocalExperimentBatchRunner(
            solver_proxy,
            experiment_configs
        ).run(process_limit=args.procs)


if __name__ == "__main__":
    pass
