///! Definitions of batch level structures
use std::path::{Path, PathBuf};

use serde::{Deserialize, Serialize};

use super::experiment::Experiment;

/// Mirroring solver config dumped in `config.json` at the batch level
#[derive(Deserialize, Serialize, Debug, Clone)]
pub struct SolverConfig {
    #[serde(rename(serialize = "inputFile"))]
    pub input_file: Option<String>,

    #[serde(rename(serialize = "outputDir"))]
    pub output_dir: Option<String>,

    #[serde(rename(serialize = "nGen"))]
    pub n_gen: usize,

    #[serde(rename(serialize = "popSize"))]
    pub pop_size: Option<usize>,

    #[serde(rename(serialize = "delayConstFactor"))]
    pub delay_const_factor: Option<f64>,

    #[serde(rename(serialize = "solverType"))]
    pub solver_type: String,
}

#[derive(Deserialize, Serialize, Debug, Clone)]
pub struct BatchConfigModel {
    #[serde(rename(serialize = "outputDir"))]
    pub output_dir: Option<PathBuf>,

    pub configs: Vec<Experiment>,

    #[serde(rename(serialize = "solverConfig"))]
    pub solver_config: Option<SolverConfig>,

    #[serde(rename(serialize = "startTime"))]
    pub start_time: Option<String>,
}

impl BatchConfigModel {
    pub fn new(
        output_dir: PathBuf,
        configs: Vec<Experiment>,
        solver_config: SolverConfig,
        start_time: String,
    ) -> Self {
        Self {
            output_dir: Some(output_dir),
            configs,
            solver_config: Some(solver_config),
            start_time: Some(start_time),
        }
    }
}

impl TryFrom<&Path> for BatchConfigModel {
    type Error = anyhow::Error;

    fn try_from(value: &Path) -> Result<Self, Self::Error> {
        if !value.is_dir() {
            anyhow::bail!(
                "Received path is not a directory: {:?}. Expected path to batch root directory",
                value
            );
        }

        todo!()
    }
}
