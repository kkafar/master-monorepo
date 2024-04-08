///! Definitions of experiment level structures

use std::path::PathBuf;

use serde::Serialize;

use super::problem::InstanceInfo;


#[derive(Serialize, Debug, Clone)]
pub struct Experiment {
    pub name: String,
    pub instnace: InstanceInfo,
    pub config: ExperimentConfig,
}

#[derive(Serialize, Debug, Clone)]
pub struct ExperimentConfig {
    pub input_file: PathBuf,
    pub output_dir: PathBuf,
    pub config_file: Option<PathBuf>,
    pub n_series: usize,
}
