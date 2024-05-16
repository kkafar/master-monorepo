from dataclasses import dataclass
from pathlib import Path
from core.util import iter_batched
from typing import Optional
from copy import copy, deepcopy


def ceildiv(a: int, b: int) -> int:
    return -(a // -b)


@dataclass
class Operation:
    id: int
    duration: int
    machine: int
    job_id: int  # I need it later for plotting
    finish_time: Optional[int] = None


@dataclass
class Job:

    # Operations have id numbered from 1 upwards, hence ops[0].id = 1, etc.
    ops: list[Operation]

    @property
    def ops_count(self) -> int:
        return len(self.ops)


@dataclass
class JsspInstance:
    """ I do not care about complexity in this class. At least for now.
    Future me will hate this. """

    # JOBS use 0-based numbering,
    # OPERATIONS use 1-based numbering,
    # MACHINES use 0-based numbering,

    inner_jobs: list[Job]

    # Machines are numbered from 0 upwards
    n_machines: int

    @property
    def jobs(self) -> list[Job]:
        return self.inner_jobs

    @property
    def n_jobs(self):
        return len(self.inner_jobs)

    @property
    def n_ops(self):
        return self.n_jobs * self.n_machines

    @staticmethod
    def job_id_of_op(op_id: int, n_jobs: int, n_ops: int) -> int:
        if op_id >= n_ops:
            raise ValueError(f"op_id ({op_id}) must not be >= n_ops {n_ops}")
        return (op_id - 1) % n_jobs

    @staticmethod
    def op_offset_in_job(op_id: int, n_jobs: int) -> int:
        """Returns which operation in turn of its job this operation is.
        Correct result should be >= 1.
        Expect garbage output for garbage input."""
        return ceildiv(op_id, n_jobs)

    @staticmethod
    def job_pred_for_op(op_id: int, n_jobs: int) -> Optional[int]:
        if op_id - n_jobs >= 1:
            return op_id - n_jobs
        return None

    @staticmethod
    def id_of_kth_op_of_job_j(k: int, j: int, n_jobs: int) -> int:
        """Returns "global" id of k'th operation of job j.
        Note that it is assumed that k >= 1.
        This method panics when k < 1.
        It **might** return invalid result for invalid input, e.g.
        when job j does not have kth operation."""
        assert k >= 1
        return (k - 1) * n_jobs + j + 1

    def job_for_op_with_id(self, op_id: int) -> Optional[Job]:
        return self.inner_jobs[JsspInstance.job_id_of_op(op_id, self.n_jobs, self.n_ops)]

    def op_for_id(self, id: int) -> Operation:
        """
        :returns: operation with given id, raises error in case op was not found
        """
        if (job := self.job_for_op_with_id(id)) is not None:
            index = JsspInstance.op_offset_in_job(id, self.n_jobs) - 1
            op = job.ops[index]
            assert op.id == id, f"Found wrong operation ({op.id}), expected ({id})"
            return op
        else:
            raise ValueError(f"Failed to found op for id {id}")

    def pred_for_op_with_id(self, id: int) -> Optional[Operation]:
        """
        :returns: None only in case op with this id is the first op of the job. Raises
        exception on other failures. In case of success returns desired operation.
        """
        if (job := self.job_for_op_with_id(id)) is not None:
            pred_id = JsspInstance.job_pred_for_op(id, self.n_jobs)
            if pred_id is not None:
                return self.op_for_id(pred_id)
            else:
                return None
        else:
            raise ValueError(f"Failed to find job for op with id {id}")

    def reset(self):
        for job in self.jobs:
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

        # Single line for each job + header
        assert len(spec) == n_jobs + 1, "It looks like there are more jobs spec than expected"

        # I want to have jobs numbered from 0, and operations numbered fom 1
        jobs: list[Job] = []

        for job_id, line in enumerate(spec[1:]):
            line = line.split()
            assert len(line) % 2 == 0, "Expected even number of elements in line with job specification"

            ops = []

            for op_number_in_job, (machine_id, duration) in enumerate(iter_batched(line, 2)):
                op_id = JsspInstance.id_of_kth_op_of_job_j(op_number_in_job + 1, job_id, n_jobs)
                ops.append(Operation(id=op_id, duration=int(duration), machine=int(machine_id), job_id=job_id, finish_time=None))

            jobs.append(Job(ops=ops))

        return JsspInstance(jobs, n_machines)


# TODO: Make use of this class when reconstructing & validating solution string
# in context of instance
@dataclass
class ScheduleReconstructionResult:
    instance: JsspInstance
    err: Optional[str]

    @property
    def ok(self) -> bool:
        return self.err is None or len(self.err) == 0


def validate_solution_string_in_context_of_instance(solstr: str, instance: JsspInstance, fitness: int, compat: bool = False) -> ScheduleReconstructionResult:
    """ Verify the solution string according to problem instance constraints. Basically we create the full
    schedule (lists of jobs in order of execution for each machine) based on solution string and instance spec.
    After building up the schedule, problem constraints are validated (jobs precedence) and the fitness value is verified
    NOTE: This method modifies the passed instance!!!

    :param solstr: solution string as outputted by solver
    :param instance: specification of the problem instance (job description, etc.)
    :param fitness: fitness the solver claims this solution has
    :param compat: whether solution string needs to be translated first, because it uses old operation numbering rules
    :returns: reconstruction result, see structure definition for details
    """

    assert solstr is not None
    assert instance is not None
    assert fitness is not None

    instance.reset()

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

    # We need to copy the instance as it is then returned and used further in processing,
    # while instance object is reset and reused and operation objects are modified.
    # We must create a deepcopy...

    makespan = find_makespan(machine_schedules)
    if makespan != fitness:
        err = f"Reconstructed solution has different fitness than reported by solver. {makespan} vs {fitness}"
        return ScheduleReconstructionResult(instance=deepcopy(instance), err=err)
    return ScheduleReconstructionResult(instance=deepcopy(instance), err=None)

