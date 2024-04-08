///! Definitions of batch level structures

use std::path::{Path, PathBuf};

use serde::Serialize;

use super::experiment::Experiment;


/// Mirroring solver config dumped in `config.json` at the batch level
#[derive(Serialize, Debug, Clone)]
pub struct SolverConfig {
    pub input_file: Option<String>,
    pub output_dir: Option<String>,
    pub n_gen: usize,
    pub pop_size: Option<usize>,
    pub delay_const_factor: Option<f64>,
    pub solver_type: String,
}


#[derive(Serialize, Debug, Clone)]
pub struct BatchConfig {
    pub output_dir: PathBuf,
    pub configs: Vec<Experiment>,
    pub solver_config: SolverConfig,
    pub start_time: String,
}

impl BatchConfig {
    pub fn new(output_dir: PathBuf, configs: Vec<Experiment>, solver_config: SolverConfig, start_time: String) -> Self {
        Self {
            output_dir,
            configs,
            solver_config,
            start_time,
        }
    }
}


impl TryFrom<&Path> for BatchConfig {
    type Error = anyhow::Error;

    fn try_from(value: &Path) -> Result<Self, Self::Error> {
        if !value.is_dir() {
            anyhow::bail!("Received path is not a directory: {:?}. Expected path to batch root directory", value);
        }



        todo!()
    }

}
