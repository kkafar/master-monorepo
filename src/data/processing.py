from pathlib import Path
from typing import Optional
from experiment.model import Experiment
from data.model import JoinedExperimentData
from .tools import experiment_data_from_all_series
from .plot import create_plots_for_experiment
from .stat import compute_per_exp_stats, compute_global_exp_stats
from core.fs import get_plotdir_for_exp, get_main_tabledir


def process_experiment_data(exp: Experiment, data: JoinedExperimentData, outdir: Optional[Path]):
    """ :param outdir: directory for saving processed data """

    print(f"Processing experiment {exp.name}")

    exp_plotdir = get_plotdir_for_exp(exp, outdir) if outdir is not None else None
    create_plots_for_experiment(exp, data, exp_plotdir)
    # compute_per_exp_stats(exp, data)


def process_experiment_batch_output(batch: list[Experiment], outdir: Optional[Path]):
    """ :param outdir: directory for saving processed data """

    data = [experiment_data_from_all_series(exp) for exp in batch]

    for exp, expdata in zip(batch, data):
        process_experiment_data(exp, expdata, outdir)

    tabledir = get_main_tabledir(outdir) if outdir is not None else None
    compute_global_exp_stats(batch, data, tabledir)

