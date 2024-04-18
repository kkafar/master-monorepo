use std::path::PathBuf;

use clap::Parser;

#[derive(Parser, Debug, Clone)]
pub struct Args {
    /// Either directory of experiment batch result or directory containing other directories
    /// with experiment batch results.
    #[arg(short = 'r', long = "results")]
    pub results_dir: Option<PathBuf>,

    /// Directory in which already processed batch results are stored.
    /// If it does not exist, it will be created and new processing results will be stored there.
    #[arg(short = 'p', long = "processed")]
    pub processed_results_dir: Option<PathBuf>,

    /// Port for the server to run on. Right now it always runs on local host.
    #[arg(long = "port")]
    pub port: Option<usize>,

    #[arg(long = "ecdk")]
    pub ecdk_dir: Option<PathBuf>,

    #[arg(short = 'c', long = "config")]
    pub config: Option<PathBuf>,
}
