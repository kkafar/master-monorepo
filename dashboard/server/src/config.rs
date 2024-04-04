use std::path::PathBuf;

use anyhow::anyhow;


#[derive(Debug, Clone)]
pub struct Config {
    /// Either directory of experiment batch result or directory containing other directories
    /// with experiment batch results.
    pub results_dir: PathBuf,

    /// Directory in which already processed batch results are stored.
    /// If it does not exist, it will be created and new processing results will be stored there.
    pub processed_results_dir: PathBuf,
}


pub struct PartialConfig {
    pub results_dir: Option<PathBuf>,
    pub processed_results_dir: Option<PathBuf>,
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
        })
    }
}

