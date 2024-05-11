from tqdm import tqdm
from cli.args import ValidateInstanceSpecArgs
from context import Context
from data.file_resolver import resolve_all_input_files
from problem import JsspInstance


def assert_each_machine_has_exact_op_count(instance: JsspInstance, expected_op_count: int):
    assert instance.n_machines > 0, "Number of machines must be positive"
    machine_ops_count = [0 for _ in range(instance.n_machines)]
    for job in instance.jobs:
        for op in job.ops:
            machine_ops_count[op.machine] += 1

    for m_id, count in enumerate(machine_ops_count):
        assert count == expected_op_count, f"Expected {expected_op_count} operations on machine {m_id}, got: {count}"


def assert_each_job_has_equal_op_count(instance: JsspInstance):
    assert instance.n_jobs > 0, "Number of jobs must be positive"
    job_count = len(instance.jobs[0].ops)
    for job in instance.jobs:
        assert len(job.ops) == job_count, f"Not all jobs have the same number of operations. Got: {len(job.ops)}, expected: {job_count}"


def validate_instance_spec(ctx: Context, args: ValidateInstanceSpecArgs):
    # Not recursive as we don't want to load Taillard specification
    input_files = resolve_all_input_files(args.input_files, recursive=False)

    print("Asserting problem invariants...")

    for file in tqdm(input_files):
        instance = JsspInstance.from_instance_file(file)
        assert_each_machine_has_exact_op_count(instance, instance.n_jobs)
        assert_each_job_has_equal_op_count(instance)

    print("All assertions passed: OK")

