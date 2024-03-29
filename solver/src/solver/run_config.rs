use crate::{problem::JsspInstance, config::Config};
use serde::Serialize;

#[derive(Serialize, Clone, Copy)]
pub struct RunConfig {
    /// Size of the population that solver should use.
    pub pop_size: usize,

    /// Number of generations for solver to run for.
    pub n_gen: usize,

    /// Elitims rate passed to JsspCrossover operator in solvers that utilise it.
    /// See JsspCrossover implementation to understand its meaning exactly.
    pub elitism_rate: f64,

    /// Sampling rate passed to JsspCrossover operator in solvers that utilise it
    /// See JsspCrossover implementation to understand its meaning exactly.
    pub sampling_rate: f64,

    /// The constant that appears in formula for delay in given iteration g.
    /// Delay = Gene_{n+g} * delay_const_factor * maxdur. If not specified, defaults to 1.5.
    pub delay_const_factor: f64,
}

impl RunConfig {
    pub fn new(instance: &JsspInstance, config: &Config) -> Self {
        Self {
            pop_size: config.pop_size.unwrap_or(instance.cfg.n_ops * 2),
            n_gen: config.n_gen.unwrap_or(400),
            elitism_rate: config.elitism_rate,
            sampling_rate: config.sampling_rate,
            delay_const_factor: config.delay_const_factor.unwrap_or(1.5),
        }
    }
}
