from typing import Optional
from pathlib import Path
from experiment.model import Experiment, ExperimentConfig, ExperimentBatch
from data.model import InstanceMetadata
from core.fs import (
    get_main_plotdir,
    get_plotdir_for_exp,
    get_main_tabledir,
    get_tabledir_for_exp,
    init_processed_data_file_hierarchy,
    initialize_file_hierarchy,
)


def create_mock_exp(exp_name: str = 'test01',
                    input_file: Optional[Path] = None,
                    output_dir: Optional[Path] = None,
                    n_series: int = 2) -> Experiment:
    return Experiment(
        name=f'{exp_name}',
        instance=InstanceMetadata(
            id=f'{exp_name}',
            ref=f'{exp_name}_ref',
            jobs=10,
            machines=10,
            lower_bound=1000,
            lower_bound_ref=f'{exp_name}_lb_ref',
            best_solution=1000,
            best_solution_ref=f'{exp_name}_bs_ref',
            best_solution_time=f'{exp_name}_bst',
            best_solution_time_ref=f'{exp_name}_bst_ref'
        ),
        config=ExperimentConfig(
            input_file=input_file or Path(f'./data/instances-mock/test_instances/{exp_name}.txt'),
            output_dir=output_dir or Path('__test__/exp_test_outdir'),
            config_file=None,
            n_series=n_series
        ),
        result=None
    )


def test_plotdir_path():
    exp = create_mock_exp()
    plot_dir = get_main_plotdir(exp.config.output_dir)
    assert plot_dir == Path('__test__/exp_test_outdir/plots')


def test_exp_plotdir_path():
    exp = create_mock_exp()
    exp_plotdir = get_plotdir_for_exp(exp, exp.config.output_dir)
    assert exp_plotdir == Path('__test__/exp_test_outdir/plots/test01')


def test_tabledir_path():
    exp = create_mock_exp()
    tabledir = get_main_tabledir(exp.config.output_dir)
    assert tabledir == Path('__test__/exp_test_outdir/tables')


def test_exp_tabledir_path():
    exp = create_mock_exp()
    exp_tabledir = get_tabledir_for_exp(exp, exp.config.output_dir)
    assert exp_tabledir == Path('__test__/exp_test_outdir/tables/test01')


def test_processed_data_file_hierarchy_creation(tmp_path):
    # Asserting that pytest works as I expect it to
    assert tmp_path is not None and isinstance(tmp_path, Path)

    exp_1 = create_mock_exp('test01')
    exp_2 = create_mock_exp('test02')

    assert not exp_1.config.output_dir.is_dir()
    assert not exp_2.config.output_dir.is_dir()

    init_processed_data_file_hierarchy([exp_1, exp_2], tmp_path)

    assert get_main_tabledir(tmp_path).is_dir()
    assert get_main_tabledir(tmp_path).is_dir()

    for exp in (exp_1, exp_2):
        assert get_plotdir_for_exp(exp, tmp_path).is_dir()


def test_run_file_hierarchy_creation(tmp_path):
    # Asserting that pytest works as I expect it to
    assert tmp_path is not None and isinstance(tmp_path, Path)

    n_series = 2
    exp_1_name = 'test01'
    exp_2_name = 'test02'
    exp_1_dir: Path = tmp_path.joinpath(exp_1_name)
    exp_2_dir: Path = tmp_path.joinpath(exp_2_name)

    exp_1 = create_mock_exp('test01', output_dir=exp_1_dir, n_series=n_series)
    exp_2 = create_mock_exp('test02', output_dir=exp_2_dir, n_series=n_series)

    batch = ExperimentBatch(output_dir=tmp_path, experiments=[exp_1, exp_2], solver_config=None)
    initialize_file_hierarchy(batch)

    assert exp_1_dir.is_dir()
    assert exp_2_dir.is_dir()

    exp_1_subdirs = list(exp_1_dir.iterdir())
    exp_2_subdirs = list(exp_2_dir.iterdir())

    # +1 because of `experiment file`
    assert len(exp_1_subdirs) == n_series + 1
    assert len(exp_2_subdirs) == n_series + 1

