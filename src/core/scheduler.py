import datetime as dt
import subprocess as sp
from typing import NamedTuple, Tuple
from time import sleep


class Task(NamedTuple):
    id: int
    process_args: Tuple | list


class CompletedTask(NamedTuple):
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
    start_time: dt.datetime
    end_time: dt.datetime

    @property
    def duration(self) -> dt.timedelta:
        return self.end_time - self.start_time


class MultiProcessTaskRunner:
    def __log_run(self, task: Task):
        print(f'[{dt.datetime.now()}][START] {task}')

    def __log_complete_success(self, task: CompletedTask):
        print(f'[{dt.datetime.now()}][COMPL] {task}')

    def __log_complete_error(self, task: CompletedTask):
        print(f'[{dt.datetime.now()}][ERROR] {task}')

    def __complete_task(self, task: RunningTask) -> CompletedTask:
        return CompletedTask(
            origin=task.origin,
            return_code=task.process.returncode,
            start_time=task.start_time,
            end_time=dt.datetime.now()
        )

    def run(self, tasks: list[Task], process_limit: int = 1, poll_interval: float = 0.1) -> tuple[list[CompletedTask], RunInfo]:
        finished_count = 0
        running_tasks = set()
        n_tasks = len(tasks)
        n_scheduled = min(process_limit, n_tasks)

        start_time = dt.datetime.now()

        for task_id, task in enumerate(tasks[:n_scheduled]):
            self.__log_run(task)
            running_tasks.add(RunningTask(
                origin=task,
                process=sp.Popen(task.process_args, stdout=sp.DEVNULL),
                start_time=dt.datetime.now()
            ))

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
                completed_task = self.__complete_task(task)
                completed_tasks[task.id] = completed_task
                just_finished_tasks.add(task)
                finished_count += 1

                if not completed_tasks.is_ok():
                    self.__log_complete_error(completed_task)
                else:
                    self.__log_complete_success(completed_task)

                # If there are any tasks left to schedule
                if n_scheduled < n_tasks:
                    task = tasks[n_scheduled]
                    self.__log_run(task)
                    just_scheduled_tasks.add(RunningTask(
                        origin=task,
                        process=sp.Popen(task.process_args, stdout=sp.DEVNULL),
                        start_time=dt.datetime.now()
                    ))
                    n_scheduled += 1

            running_tasks.difference_update(just_finished_tasks)
            running_tasks.update(just_scheduled_tasks)

            if len(running_tasks) == 0:
                break
            else:
                sleep(poll_interval)

        end_time = dt.datetime.now()
        runinfo = RunInfo(start_time, end_time)

        assert len(completed_tasks) == n_tasks

        print(f"Completed batch of {len(tasks)} in {runinfo.duration}")
        return completed_tasks, runinfo

