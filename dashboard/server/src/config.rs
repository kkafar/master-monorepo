use std::{io::BufReader, path::PathBuf};

use anyhow::anyhow;
use serde::Deserialize;

use crate::cli::Args;

#[derive(Debug, Clone, Deserialize)]
pub struct Config {
    /// Either directory of experiment batch result or directory containing other directories
    /// with experiment batch results.
    pub results_dir: PathBuf,

    /// Directory in which already processed batch results are stored.
    /// If it does not exist, it will be created and new processing results will be stored there.
    pub processed_results_dir: PathBuf,

    /// Port for the server to run on. Right now it always runs on local host.
    pub port: usize,

    /// Directory of ecdk project
    pub ecdk_dir: PathBuf,
}

impl Config {
    pub fn try_from_args(args: &Args) -> anyhow::Result<Self> {
        Self::try_from(PartialConfig::from_args(args))
    }
}

#[derive(serde::Deserialize)]
pub struct PartialConfig {
    pub results_dir: Option<PathBuf>,
    pub processed_results_dir: Option<PathBuf>,
    pub port: Option<usize>,
    pub ecdk_dir: Option<PathBuf>,
}

impl PartialConfig {
    pub fn empty() -> Self {
        Self {
            results_dir: None,
            processed_results_dir: None,
            port: None,
            ecdk_dir: None,
        }
    }

    pub fn from_args(args: &Args) -> Self {
        let file_content: PartialConfig =
        if let Some(ref cfg_file) = args.config {
            if let Ok(file) = std::fs::File::open(cfg_file) {
                let reader = BufReader::new(file);
                serde_json::from_reader(reader).unwrap_or(Self::empty())
            } else {
                Self::empty()
            }
        } else {
            Self::empty()
        };

        Self {
            results_dir: args.results_dir.clone().or(file_content.results_dir),
            processed_results_dir: args.processed_results_dir.clone().or(file_content.processed_results_dir),
            port: args.port.clone().or(file_content.port),
            ecdk_dir: args.ecdk_dir.clone().or(file_content.ecdk_dir),
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

        if !partial_cfg.ecdk_dir.is_some() {
            return Err(anyhow!("Ecdk directory must be provided"));
        }

        Ok(Config {
            results_dir,
            processed_results_dir,
            port: partial_cfg.port.unwrap_or(8088),
            ecdk_dir: partial_cfg.ecdk_dir.unwrap(),
        })
    }
}
