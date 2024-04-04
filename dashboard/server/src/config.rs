use std::path::PathBuf;

use anyhow::anyhow;

use crate::cli::Args;


#[derive(Debug, Clone)]
pub struct Config {
    /// Either directory of experiment batch result or directory containing other directories
    /// with experiment batch results.
    pub results_dir: PathBuf,

    /// Directory in which already processed batch results are stored.
    /// If it does not exist, it will be created and new processing results will be stored there.
    pub processed_results_dir: PathBuf,

    /// Port for the server to run on. Right now it always runs on local host.
    pub port: usize,
}

impl Config {
    pub fn try_from_args(args: &Args) -> anyhow::Result<Self> {
        Self::try_from(PartialConfig::from_args(args))
    }
}

pub struct PartialConfig {
    pub results_dir: Option<PathBuf>,
    pub processed_results_dir: Option<PathBuf>,
    pub port: Option<usize>,
}

impl PartialConfig {
    pub fn from_args(args: &Args) -> Self {
        Self {
            results_dir: Some(args.results_dir.clone()),
            processed_results_dir: Some(args.processed_results_dir.clone()),
            port: args.port.clone(),
        }
    }
}

impl TryFrom<PartialConfig> for Config {
    type Error = anyhow::Error;

    fn try_from(partial_cfg: PartialConfig) -> Result<Self, Self::Error> {
        let Some(results_dir) = partial_cfg.results_dir else {
            return Err(anyhow!("Results dir must be provided"));
        };

        let Some(processed_results_dir) = partial_cfg.processed_results_dir else {
            return Err(anyhow!("Processed results dir must be provided"));
        };

        if !results_dir.is_dir() {
            return Err(anyhow!("Provided results directory is not a directory!"));
        }

        Ok(Config {
            results_dir,
            processed_results_dir,
            port: partial_cfg.port.unwrap_or(8088),
        })
    }
}

