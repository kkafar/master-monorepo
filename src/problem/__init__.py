from dataclasses import dataclass
from pathlib import Path
from core.util import iter_batched
from typing import Optional
from pprint import pprint


@dataclass()
class IdSpan:
    start: int
    end: int

    def __contains__(self, item: int) -> bool:
        return item >= self.start and item <= self.end


@dataclass
class Operation:
    id: int
    duration: int
    machine: int
    job_id: int  # I need it later for plotting
    finish_time: Optional[int] = None


@dataclass
class Job:
    ops: list[Operation]  # ops[0] = None, ops are numbered from 1
    span: IdSpan


@dataclass
class JsspInstance:
    """ I do not care about complexity in this class. At least for now.
    Future me will hate this. """

    jobs: list[Job]
    n_machines: int

    @property
    def n_jobs(self):
        return len(self.jobs)

    def job_for_op_with_id(self, opid: int) -> Optional[Job]:
        for job in self.jobs[1:]:
            if opid in job.span:
                return job
        return None

    def op_for_id(self, id: int) -> Operation:
        """
        :returns: operation with given id, raises error in case op was not found
        """
        if (job := self.job_for_op_with_id(id)) is not None:
            op = job.ops[id - job.span.start]
            assert op.id == id
            return op
        else:
            raise ValueError(f"Failed to found op for id {id}")

    def pred_for_op_with_id(self, id: int) -> Optional[Operation]:
        """
        :returns: None only in case op with this id is the first op of the job. Raises
        exception on other failures. In case of success returns desired operation.
        """
        if (job := self.job_for_op_with_id(id)) is not None:
            # looking for pred
            if id - 1 >= job.span.start:
                return job.ops[id - job.span.start - 1]
            else:
                return None
        else:
            raise ValueError(f"Failed to find job for op with id {id}")

    def reset(self):
        for job in self.jobs[1:]:
            for op in job.ops:
                op.finish_time = None

    @staticmethod
    def from_instance_file(file: Path) -> 'JsspInstance':
        assert file.is_file(), f"File {file} does not exist"

        spec: list[str] = None
        with open(file, 'r') as file:
            spec = file.readlines()

        assert spec is not None, "Failed to load instance file content"

        first_line = spec[0].split()
        assert len(first_line) == 2, f"Expected 2 elements in first line of the instance file, found {len(first_line)}"

        n_jobs, n_machines = int(first_line[0]), int(first_line[1])

        assert len(spec) == n_jobs + 1, "It looks like there are more jobs spec than expected"

        # I want to have jobs numbered from 1, as it is done in the solution string
        jobs: list[Job] = [None]
        crt_op_id = 1
        crt_job_id = 1

        for line_i, line in enumerate(spec[1:]):
            line = line.split()
            assert len(line) % 2 == 0, "Expected even number of elements in line with job specification"

            first_op_id = crt_op_id
            ops = []

            for machine_id, duration in iter_batched(line, 2):
                ops.append(Operation(id=crt_op_id, duration=int(duration), machine=int(machine_id), job_id=crt_job_id, finish_time=None))
                crt_op_id += 1

            crt_job_id += 1
            last_op_id = crt_op_id - 1
            jobs.append(Job(ops=ops, span=IdSpan(first_op_id, last_op_id)))

        return JsspInstance(jobs, n_machines)


def validate_solution_string_in_context_of_instance(solstr: str, instance: JsspInstance, fitness: int) -> tuple[bool, list[list[Operation]], str]:
    """ Verify the solution string according to problem instance constraints. Basically we create the full
    schedule (lists of jobs in order of execution for each machine) based on solution string and instance spec.
    After building up the schedule, problem constraints are validated (jobs precedence) and the fitness value is verified
    NOTE: This method modifies the passed instance!!!

    :param solstr: solution string as outputted by solver
    :param instance: specification of the problem instance (job description, etc.)
    :param fitness: fitness the solver claims this solution has
    :returns: tuple of three elements:
        1. True if the reconstructed solution satisfies problem constraints and it has the same fitness as claimed by the solver. False otherwise.
        2. reconstructed schedule for each machine
        3. error message if the schedule is not valid
    """

    assert solstr is not None
    assert instance is not None
    assert fitness is not None

    def last_schedule_time_for_machine(machines: list[list[Operation]], mid: int) -> int:
        machine = machines[mid]
        if len(machine) == 0:
            return 0

        ft = machines[mid][-1].finish_time
        assert ft is not None, "Finish time of scheduled operation must not be None"
        return ft

    def find_makespan(machines: list[list[Operation]]) -> int:
        return max(map(lambda m: m[-1].finish_time, machines))

    # Jobs in order of their finish time. In case of tie, operation with lower machine index is first.
    # There is also special ordering rule for operations with 0 duration. Take a look into the docs of this repo
    # on the data model
    ordered_op_ids = list(map(int, solstr.split('_')))

    machine_schedules = [[] for _ in range(0, instance.n_machines)]

    for id in ordered_op_ids:
        if (op := instance.op_for_id(id)) is not None:
            # We need to find direct predecessor of this op and confirm that it has already
            # been scheduled...
            pred = instance.pred_for_op_with_id(id)
            pred_ft = 0
            if pred is not None:
                assert pred.finish_time is not None, f"Predecesor {pred.id} of op {op.id} has not been scheduled yet"
                pred_ft = pred.finish_time
            machine_earliest_schedule_time = last_schedule_time_for_machine(machine_schedules, op.machine)
            earliest_schedule_time = max(machine_earliest_schedule_time, pred_ft)
            op.finish_time = earliest_schedule_time + op.duration
            machine_schedules[op.machine].append(op)
        else:
            raise ValueError(f"Received None for op with id: {id}")

    # pprint(machine_schedules)
    makespan = find_makespan(machine_schedules)
    if makespan != fitness:
        err = f"Reconstructed solution has different fitness than reported by solver. {makespan} vs {fitness}"
        return False, machine_schedules, err
    return True, machine_schedules, ""

