use std::{error::Error, fs::File, io::BufReader, path::PathBuf};

use serde::Deserialize;

use crate::cli::Args;

pub const SOLVER_TYPE_DEFAULT: &str = "default";
pub const SOLVER_TYPE_RANDOMSEARCH: &str = "randomsearch";
pub const SOLVER_TYPE_MIDPOINT: &str = "midpoint";
pub const SOLVER_TYPE_DOUBLED_CROSSOVER: &str = "double_singlepoint";
pub const SOLVER_TYPE_DOUBLED_RANK: &str = "double_rank";

/// This struct is mirrored inside ecdk's code by
/// `SolverConfigFileContents` method. Update it accordingly.
#[derive(Debug, Clone)]
pub struct Config {
    /// Path to file with instance specification
    pub input_file: PathBuf,

    /// Path to directory where the solver's output should be put
    pub output_dir: PathBuf,

    /// Number of generations. Set this if you want to override
    /// the default value
    pub n_gen: Option<usize>,

    /// Number of individuals in population. Set this if you want to
    /// override the default value computed basing on problem size
    pub pop_size: Option<usize>,

    /// The constant that appears in formula for delay in given iteration g.
    /// Delay = Gene_{n+g} * delay_const_factor * maxdur. If not specified, defaults to 1.5.
    pub delay_const_factor: Option<f64>,

    /// Solver type to run. Available options: `default`, `randomsearch`, `midpoint`, `double_singlepoint`.
    pub solver_type: String,

    /// Elitims rate passed to JsspCrossover operator in solvers that utilise it.
    /// See JsspCrossover implementation to understand its meaning exactly.
    pub elitism_rate: f64,

    /// Sampling rate passed to JsspCrossover operator in solvers that utilise it
    /// See JsspCrossover implementation to understand its meaning exactly.
    pub sampling_rate: f64,

    /// Whether the Nowicki & Smutnicki local search operator should be used
    /// in an attempt to improve makespan. Note that this is utilised only
    /// by solvers that do use "standard" JsspFitness.
    pub local_search_enabled: Option<bool>,
}

#[derive(Deserialize, Debug, Clone)]
pub struct PartialConfig {
    pub input_file: Option<PathBuf>,
    pub output_dir: Option<PathBuf>,
    pub n_gen: Option<usize>,
    pub pop_size: Option<usize>,
    pub delay_const_factor: Option<f64>,
    pub solver_type: Option<String>,
    pub elitism_rate: Option<f64>,
    pub sampling_rate: Option<f64>,
    pub local_search_enabled: Option<bool>,
}

impl PartialConfig {
    pub fn empty() -> PartialConfig {
        Self {
            input_file: None,
            output_dir: None,
            n_gen: None,
            pop_size: None,
            delay_const_factor: None,
            solver_type: None,
            elitism_rate: None,
            sampling_rate: None,
            local_search_enabled: None,
        }
    }
}

impl TryFrom<PathBuf> for PartialConfig {
    type Error = Box<dyn Error>;

    fn try_from(path: PathBuf) -> Result<Self, Self::Error> {
        let reader = BufReader::new(File::open(path)?);
        let cfg: PartialConfig = serde_json::from_reader(reader)?;
        Ok(cfg)
    }
}

impl TryFrom<PartialConfig> for Config {
    type Error = String;

    fn try_from(partial_cfg: PartialConfig) -> Result<Self, Self::Error> {
        if partial_cfg.input_file.is_none() {
            return Err("Input file must be provided".to_owned());
        }
        if partial_cfg.output_dir.is_none() {
            return Err("Output directory must be provided".to_owned());
        }
        Ok(Self {
            input_file: partial_cfg.input_file.unwrap(),
            output_dir: partial_cfg.output_dir.unwrap(),
            n_gen: partial_cfg.n_gen,
            pop_size: partial_cfg.pop_size,
            delay_const_factor: partial_cfg.delay_const_factor,
            solver_type: partial_cfg
                .solver_type
                .unwrap_or(String::from(SOLVER_TYPE_DEFAULT)),
            elitism_rate: partial_cfg.elitism_rate.unwrap_or(0.1), // Defaults from paper
            sampling_rate: partial_cfg.sampling_rate.unwrap_or(0.2), // Defaults from paper
            local_search_enabled: partial_cfg.local_search_enabled,
        })
    }
}

impl TryFrom<Args> for Config {
    type Error = String;

    fn try_from(args: Args) -> Result<Self, Self::Error> {
        let mut partial_cfg = if let Some(ref cfg_file) = args.cfg_file {
            match PartialConfig::try_from(cfg_file.to_owned()) {
                Ok(cfg) => cfg,
                Err(err) => return Err(format!("Error while loading config from file: {}", err)),
            }
        } else {
            PartialConfig::empty()
        };

        if let Some(input_file) = args.input_file {
            partial_cfg.input_file = Some(input_file);
        }
        if let Some(output_dir) = args.output_dir {
            partial_cfg.output_dir = Some(output_dir);
        }
        if let Some(n_gen) = args.n_gen {
            partial_cfg.n_gen = Some(n_gen);
        }
        if let Some(pop_size) = args.pop_size {
            partial_cfg.pop_size = Some(pop_size);
        }
        if let Some(factor) = args.delay_const_factor {
            partial_cfg.delay_const_factor = Some(factor);
        }
        if let Some(solver_type) = args.solver_type {
            partial_cfg.solver_type = Some(solver_type);
        }
        if let Some(elitism_rate) = args.elitism_rate {
            partial_cfg.elitism_rate = Some(elitism_rate);
        }
        if let Some(sampling_rate) = args.sampling_rate {
            partial_cfg.sampling_rate = Some(sampling_rate);
        }
        if let Some(local_search_enabled) = args.local_search_enabled {
            partial_cfg.local_search_enabled = Some(local_search_enabled);
        }

        Config::try_from(partial_cfg)
    }
}
