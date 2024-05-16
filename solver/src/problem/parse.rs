use std::{
    io::{BufReader, Read},
    path::PathBuf,
};

use itertools::Itertools;
use thiserror::Error;

use crate::problem::{Edge, EdgeKind, JsspConfig, JsspInstance, JsspInstanceMetadata, Operation};

pub type Result<T> = std::result::Result<T, JsspInstanceLoadingError>;
pub type Error = JsspInstanceLoadingError;

#[derive(Debug, Clone, Error)]
pub enum JsspInstanceLoadingError {
    #[error("File does not exist: {0}")]
    FileDoesNotExist(String),
}

impl TryFrom<&PathBuf> for JsspInstance {
    type Error = JsspInstanceLoadingError;

    fn try_from(path: &PathBuf) -> Result<Self> {
        let name = path.file_stem().unwrap().to_str().unwrap();

        // TODO: Handle other types of errors here and do not lie to the user in general...
        let Ok(file) = std::fs::OpenOptions::new().read(true).open(path) else {
            return Err(Error::FileDoesNotExist(path.to_str().unwrap().to_owned()));
        };

        let mut reader = BufReader::new(file);
        let mut line_buffer = String::new();
        assert!(reader.read_to_string(&mut line_buffer).is_ok());

        // Read first line with n_jobs, n_machines
        let first_line = line_buffer
            .lines()
            .take(1)
            .last()
            .unwrap()
            .split_whitespace()
            .map(|n_str| n_str.parse::<usize>().unwrap())
            .collect_vec();

        assert!(
            first_line.len() == 2,
            "The first line should be composed of two, space separated numbers"
        );

        let n_jobs = first_line[0];
        let n_machines = first_line[1];

        // I've verified in https://github.com/kkafar/master-monorepo/pull/276
        // that each job has exacly n_machines operations and each machine has
        // exacly n_jobs operations.
        let expected_op_count = n_jobs * n_machines;

        // IMPORTANT:
        // Complying to https://github.com/kkafar/master-monorepo/discussions/277,
        // JOBS use 0-based numbering,
        // OPERATIONS use 1-based numbering,
        // MACHINES use 0-based numbering.
        // Moreover, since https://github.com/kkafar/master-monorepo/issues/223
        // operations are numbered in specific way. See the issue for details.

        let mut jobs: Vec<Vec<Operation>> = Vec::from_iter(
            std::iter::repeat_with(|| Vec::<Operation>::with_capacity(n_machines)).take(n_jobs),
        );

        // Processed operations counter
        let mut op_count = 0;

        line_buffer
            .lines()
            .skip(1)
            .zip_eq(jobs.iter_mut())
            .enumerate()
            .for_each(|(job_id, (job_def, job_container))| {
                job_def
                    .split_whitespace()
                    .collect_vec()
                    .chunks(2)
                    .enumerate()
                    .for_each(|(op_id_in_job, op_def)| {
                        let machine_id = op_def[0].parse().unwrap();
                        let duration = op_def[1].parse().unwrap();
                        // We add 1 because ops are 1-base indexed & enumerator starts from 0.
                        let op_id = JsspInstance::id_of_kth_op_of_job_j(op_id_in_job + 1, job_id, n_jobs);
                        let mut operation = Operation::new(
                            op_id,
                            duration,
                            machine_id,
                            None,
                            JsspInstance::generate_predecessors_of_op_with_id(op_id, n_jobs),
                        );
                        if let Some(succ_id) = JsspInstance::job_succ_of_op(op_id, n_jobs, expected_op_count)
                        {
                            operation.edges_out.push(Edge::new(succ_id, EdgeKind::JobSucc));
                        }
                        job_container.push(operation);
                        op_count += 1;
                    });
            });

        // I've verified in https://github.com/kkafar/master-monorepo/pull/276
        // that each job has exacly n_machines operations and each machine has
        // exacly n_jobs operations, thus this assertion should hold.
        assert_eq!(op_count, expected_op_count);

        Ok(JsspInstance {
            jobs,
            cfg: JsspConfig {
                n_jobs,
                n_machines,
                n_ops: expected_op_count,
            },
            metadata: JsspInstanceMetadata {
                name: name.to_owned(),
            },
        })
    }
}

#[cfg(test)]
mod tests {
    use std::{path::PathBuf, str::FromStr};

    use itertools::Itertools;

    use crate::problem::{Edge, EdgeKind, JsspInstance};

    fn get_instance_test01() -> JsspInstance {
        let path = PathBuf::from_str("data/instances/mock_instances/test01.txt").unwrap();
        let instance_loading_result = JsspInstance::try_from(&path);
        assert!(instance_loading_result.is_ok());
        instance_loading_result.unwrap()
    }

    fn get_instance_test03() -> JsspInstance {
        let path = PathBuf::from_str("data/instances/mock_instances/test03.txt").unwrap();
        let instance_loading_result = JsspInstance::try_from(&path);
        assert!(instance_loading_result.is_ok());
        instance_loading_result.unwrap()
    }

    #[test]
    fn operations_have_correct_ids_test01() {
        let instance = get_instance_test01();

        assert_eq!(instance.cfg.n_jobs, 2);
        assert_eq!(instance.cfg.n_machines, 2);
        assert_eq!(instance.cfg.n_ops, 4);
        assert_eq!(instance.jobs.len(), 2);

        {
            let job_0 = &instance.jobs[0];
            assert_eq!(job_0.len(), 2);

            let op_1 = &job_0[0];
            assert_eq!(op_1.id, 1);
            assert_eq!(op_1.machine, 1);
            assert_eq!(op_1.duration, 4);

            let op_2 = &job_0[1];
            assert_eq!(op_2.id, 3);
            assert_eq!(op_2.machine, 0);
            assert_eq!(op_2.duration, 2);
        }

        {
            let job_1 = &instance.jobs[1];
            assert_eq!(job_1.len(), 2);

            let op_1 = &job_1[0];
            assert_eq!(op_1.id, 2);
            assert_eq!(op_1.machine, 0);
            assert_eq!(op_1.duration, 1);

            let op_2 = &job_1[1];
            assert_eq!(op_2.id, 4);
            assert_eq!(op_2.machine, 1);
            assert_eq!(op_2.duration, 3);
        }
    }

    #[test]
    fn operations_have_correct_ids_test03() {
        let instance = get_instance_test03();

        assert_eq!(instance.cfg.n_jobs, 3);
        assert_eq!(instance.cfg.n_machines, 4);
        assert_eq!(instance.cfg.n_ops, 12);

        assert_eq!(instance.cfg.n_jobs, instance.jobs.len());

        let job_0_expected_ids = [1, 4, 7, 10];
        let job_1_expected_ids = [2, 5, 8, 11];
        let job_2_expected_ids = [3, 6, 9, 12];
        let job_expected_ids = [job_0_expected_ids, job_1_expected_ids, job_2_expected_ids];

        assert_eq!(job_expected_ids.len(), instance.jobs.len());

        for (_job_id, (expected_ids, actual_ids)) in job_expected_ids.iter().zip_eq(instance.jobs).enumerate()
        {
            for (&expected_id, actual_id) in expected_ids.iter().zip_eq(actual_ids.iter().map(|op| op.id)) {
                assert_eq!(expected_id, actual_id);
            }
        }
    }

    #[test]
    fn forward_job_edges_are_added_correctly_test03() {
        let instance = get_instance_test03();

        let n_jobs = instance.cfg.n_jobs;
        let n_ops = instance.cfg.n_ops;

        for job_operations in instance.jobs {
            for operation in job_operations {
                if let Some(succ_id) = JsspInstance::job_succ_of_op(operation.id, n_jobs, n_ops) {
                    assert_eq!(operation.edges_out.len(), 1);
                    assert_eq!(operation.edges_out[0], Edge::new(succ_id, EdgeKind::JobSucc));
                } else {
                    assert!(operation.edges_out.is_empty());
                }
            }
        }
    }

    #[test]
    fn predecessors_are_generated_correctly_test03() {
        let instance = get_instance_test03();

        let job_0_expected_ids = [1, 4, 7, 10];
        let job_1_expected_ids = [2, 5, 8, 11];
        let job_2_expected_ids = [3, 6, 9, 12];
        let job_expected_ids = [job_0_expected_ids, job_1_expected_ids, job_2_expected_ids];

        for (expected_job_operation_ids, actual_job_operations) in job_expected_ids.into_iter().zip_eq(instance.jobs) {
            for (i, operation) in actual_job_operations.into_iter().enumerate() {
                if i == 0 {
                    assert!(operation.preds.is_empty());
                } else {
                    assert!(!operation.preds.is_empty());
                    assert_eq!(operation.preds.len(), i);
                    operation.preds.into_iter().zip(expected_job_operation_ids).for_each(|(pred_id, expected_pred_id)| {
                        assert_eq!(expected_pred_id, pred_id);
                    });
                }
            }
        }
    }
}
