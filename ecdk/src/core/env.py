import os
from typing import Callable, Optional, TypeVar, Literal
from pathlib import Path

RT_LOCAL = 'local'
RT_ARES = 'ares'
RT_UNKNOWN = 'unknown'
RuntimeName = Literal[RT_ARES] | Literal[RT_LOCAL] | Literal[RT_UNKNOWN]


T = TypeVar('T')


class ArrayJobSpec:
    def __init__(self):
        """ I believe this is id of main job, that was used to schedule the job-array """
        self.array_job_id: Optional[int] = getmap_env('SLURM_ARRAY_JOB_ID', int)

        """ This is total number of jobs that will be scheduled in job-array. It must be zero-indexed. """
        self.array_task_count: Optional[int] = getmap_env('SLURM_ARRAY_TASK_COUNT', int)

        """ ID if the job we are currently in """
        self.array_task_id: Optional[int] = getmap_env('SLURM_ARRAY_TASK_ID', int)

    def last_task_id(self) -> Optional[int]:
        return self.array_task_count - 1


def input_range_from_jobspec(spec: ArrayJobSpec, solver_task_count: int) -> list[int]:
    """ Computes the range this job / task is responsible for.

        :param spec: spec for this job
        :param solver_task_count: number of total task that need to be run (number of input files * number of series in each exp)
        :returns: list of indices for this job"""

    assert spec.array_task_count is not None and spec.array_task_id is not None, "Task count & task id must not be None"

    tasks_per_job: int = solver_task_count // spec.array_task_count
    remaining_jobs: int = solver_task_count % spec.array_task_count

    assert tasks_per_job > 0, f"Number of tasks per job must be > 0. Jobs: {spec.array_task_count}, solver tasks: {solver_task_count}"

    start = spec.array_task_id * tasks_per_job
    end = (spec.array_task_id + 1) * tasks_per_job
    ind_range = list(range(start, end))

    if remaining_jobs > 0 and spec.array_task_id < remaining_jobs:
        additional_job = spec.last_task_id() * tasks_per_job + spec.array_task_id
        ind_range.append(additional_job)

    return ind_range


def getmap_env(var: str, mapfunc: Callable[[str], T]) -> Optional[T]:
    var_as_str = os.getenv(var, None)
    if var_as_str is None:
        return None

    return mapfunc(var_as_str)


def get_runtime_name() -> RuntimeName:
    """ Hacky way to detect whether we are running on Ares or not """
    username = os.getenv('USER', default=None)
    if username is None:
        return RT_UNKNOWN
    elif username.startswith('plg'):
        return RT_ARES
    else:
        return RT_LOCAL


def is_running_on_ares() -> bool:
    return get_runtime_name() == RT_ARES


class EnvContext:
    def __init__(self, strict: bool = False):
        self.runtime: RuntimeName = get_runtime_name()
        self.is_ares: bool = self.runtime == RT_ARES
        self.repo_dir: Optional[Path] = getmap_env('MY_MASTER_REPO', Path)
        self.short_term_cache_dir: Optional[Path] = getmap_env('MY_SCRATCH', Path)
        self.long_term_cache_dir: Optional[Path] = getmap_env('MY_GROUPS_STORAGE', Path)
        self.instance_metadata_file: Optional[Path] = getmap_env('MY_INSTANCE_METADATA_FILE', Path)
        self.instances_root_dir: Optional[Path] = getmap_env('MY_INSTANCES_DIR', Path)

        if strict:
            assert self.runtime != RT_UNKNOWN
            assert self.repo_dir is not None and self.repo_dir.is_dir()
            assert self.short_term_cache_dir is not None and self.short_term_cache_dir.is_dir()
            assert self.long_term_cache_dir is not None and self.long_term_cache_dir.is_dir()
            assert self.instance_metadata_file is not None and self.instance_metadata_file.is_file()
            assert self.instances_root_dir is not None and self.instances_root_dir.is_dir()

