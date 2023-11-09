import datetime as dt
import subprocess as sp
from typing import NamedTuple, Tuple, Dict
from time import sleep
from pathlib import Path


class Task(NamedTuple):
    ''' Represents single task that can be run in a separate process.
        First element of `process_args` should be the program name.
        This collection will be passed directly to Popen call as first argument. '''
    id: int
    process_args: Tuple | list
    stdout_file: Path


class CompletedTask(NamedTuple):
    ''' Represents single completed task, succeeded or failed, with some associated
        run information. '''
    origin: Task
    return_code: int
    start_time: dt.datetime
    end_time: dt.datetime

    @property
    def duration(self) -> dt.timedelta:
        return self.end_time - self.start_time

    @property
    def id(self) -> int:
        return self.origin.id

    def is_ok(self) -> bool:
        return self.return_code is not None and self.return_code == 0


class RunningTask(NamedTuple):
    ''' Represents task that is currently running on associated process.
        The process might be already completed. '''
    origin: Task
    process: sp.Popen
    start_time: dt.datetime

    @property
    def id(self) -> int:
        return self.origin.id

    def __eq__(self, other):
        return self.origin.id == other.origin.id

    def __hash__(self):
        return self.origin.id


class RunInfo(NamedTuple):
    ''' Metadata on the TaskRunner run. '''
    start_time: dt.datetime
    end_time: dt.datetime
    success_count: int
    failed_count: int

    @property
    def duration(self) -> dt.timedelta:
        return self.end_time - self.start_time


class MultiProcessTaskRunner:
    ''' Runs collection on tasks on limited pool of processes. To be exact
        each task is run in separate process, however the number of processes
        run simultaneously can be limited via appriopriate parameters. '''

    def __log_run(self, task: Task):
        print(f'[{dt.datetime.now()}][START] {task}')

    def __log_complete_success(self, task: CompletedTask):
        print(f'[{dt.datetime.now()}][COMPL] {task}')

    def __log_complete_error(self, task: CompletedTask):
        print(f'[{dt.datetime.now()}][ERROR] {task}')

    def __complete_task(self, task: RunningTask, fileobjs: Dict[int, object]) -> CompletedTask:
        file = fileobjs.get(task.id)
        if file is not None:
            file.close()
            del fileobjs[task.id]

        return CompletedTask(
            origin=task.origin,
            return_code=task.process.returncode,
            start_time=task.start_time,
            end_time=dt.datetime.now()
        )

    def __schedule_task(self, task: Task, task_collection: set[RunningTask], fileobjs: Dict[int, object]):
        file = None
        if task.stdout_file is not None:
            # TODO: handle the errors somehow
            file = open(task.stdout_file, 'w')
            fileobjs[task.id] = file
        task_collection.add(RunningTask(
            origin=task,
            process=sp.Popen(task.process_args, stdout=file if file is not None else sp.DEVNULL, stderr=sp.STDOUT),
            start_time=dt.datetime.now()
        ))

    def run(self, tasks: list[Task], process_limit: int = 1, poll_interval: float = 0.1) -> tuple[list[CompletedTask], RunInfo]:
        ''' Runs list of `tasks` in parallel, each task on separate process. Number of processes running simultaneously
            is limited by the `process_limit` param. The scheduling algorithm is based on primitive spinlock. Nothing sophisticated.
            The processes are queried every `poll_interval` seconds for their completion status, and then if any processes
            were found to be completed, new processes are started in their place.

            Please note that each task MUST have unique id from the set {0, 1, len(tasks) - 1}. This invariant is not verified, and must be
            satisfied by the caller.

            The results in output array of completed tasks are in order of task ids.

            :param tasks: list of tasks to perform
            :param process_limit: upper bound for number of simultaneously running processes
            :param poll_interval: spinlock interval in seconds
            :returns: tuple of 1. list of completed tasks, 2. some metrics for whole batch '''
        finished_count = 0
        failed_count = 0
        running_tasks = set()
        n_tasks = len(tasks)
        n_scheduled = min(process_limit, n_tasks)

        start_time = dt.datetime.now()

        # Note that at most :param process_limit descriptios are open at the same time
        fileobjs = {}

        for task_id, task in enumerate(tasks[:n_scheduled]):
            self.__log_run(task)
            self.__schedule_task(task, running_tasks, fileobjs)

        just_scheduled_tasks: set[RunningTask] = set()
        just_finished_tasks: set[RunningTask] = set()
        completed_tasks: list[CompletedTask] = [-1 for _ in range(n_tasks)]

        while True:
            just_scheduled_tasks.clear()
            just_finished_tasks.clear()

            for task in running_tasks:
                return_code = task.process.poll()

                # If the process has not completed yet, let it run
                if return_code is None:
                    continue

                # The process has completed
                completed_task = self.__complete_task(task, fileobjs)
                completed_tasks[task.id] = completed_task
                just_finished_tasks.add(task)
                finished_count += 1

                if not completed_task.is_ok():
                    self.__log_complete_error(completed_task)
                    failed_count += 1
                else:
                    self.__log_complete_success(completed_task)

                # If there are any tasks left to schedule
                if n_scheduled < n_tasks:
                    task = tasks[n_scheduled]
                    self.__log_run(task)
                    self.__schedule_task(task, just_scheduled_tasks, fileobjs)
                    n_scheduled += 1

            running_tasks.difference_update(just_finished_tasks)
            running_tasks.update(just_scheduled_tasks)

            if len(running_tasks) == 0:
                break
            else:
                sleep(poll_interval)

        end_time = dt.datetime.now()
        runinfo = RunInfo(start_time, end_time, n_tasks - failed_count, failed_count)

        assert len(completed_tasks) == n_tasks

        print(f"Completed batch of {len(tasks)} (OK: {runinfo.success_count}, ERR: {runinfo.failed_count}) in {runinfo.duration}")
        return completed_tasks, runinfo

