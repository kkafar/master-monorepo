from .args import AnalyzeCmdArgs
from experiment.model import Experiment
from data.processing import process_experiment_batch_output
from data.tools import extract_experiments_from_dir
from core.fs import init_processed_data_file_hierarchy
from core.env import EnvContext


def analyze(ctx: EnvContext, args: AnalyzeCmdArgs):
    experiment_batch: list[Experiment] = extract_experiments_from_dir(args.dir)

    if args.output_dir is not None:
        init_processed_data_file_hierarchy(experiment_batch, args.output_dir)

    process_experiment_batch_output(experiment_batch, args.output_dir, args.procs, args.plot)
