use std::{
    io::{BufReader, Read},
    path::PathBuf,
};

use itertools::Itertools;
use thiserror::Error;

use crate::problem::{JsspConfig, JsspInstance, JsspInstanceMetadata, Operation};

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

        let mut jobs: Vec<Vec<Operation>> = Vec::new();
        let mut op_id: usize = 0;
        let mut job_id: usize = 0;

        line_buffer.lines().skip(1).for_each(|job_def| {
            let first_job_in_batch = op_id;
            jobs.push(Vec::new());
            job_def
                .split_whitespace()
                .collect_vec()
                .chunks(2)
                .for_each(|op_def| {
                    jobs.last_mut().unwrap().push(Operation::new(
                        op_id,
                        op_def[1].parse().unwrap(),
                        op_def[0].parse().unwrap(),
                        None,
                        Vec::from_iter(first_job_in_batch..op_id),
                    ));
                    op_id += 1;
                });
            job_id += 1;
        });

        let cfg = JsspConfig {
            n_jobs: first_line[0],
            n_machines: first_line[1],
            n_ops: op_id,
        };

        Ok(JsspInstance {
            jobs,
            cfg,
            metadata: JsspInstanceMetadata {
                name: name.to_owned(),
            },
        })
    }
}
