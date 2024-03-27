use std::{rc::Rc, cell::RefCell};

pub trait StatsAware<'stats> {
    fn set_stats_engine(&mut self, engine: &'stats StatsEngine);
}

pub struct Stats {
    age_sum: usize,
    individual_count: usize,
    crossover_involvement_max: usize,
    crossover_involvement_min: usize,
}

impl Stats {
    pub fn new(age_sum: usize, individual_count: usize) -> Self {
        Self {
            age_sum,
            individual_count,
            crossover_involvement_max: usize::MIN,
            crossover_involvement_min: usize::MAX,
        }
    }
}

impl Default for Stats {
    fn default() -> Self {
        Self::new(0, 0)
    }
}

pub struct StatsEngine {
    pub stats: Rc<RefCell<Stats>>
}

impl StatsEngine {
    pub fn new() -> Self {
        Self {
            stats: Rc::new(RefCell::new(Stats::default())),
        }
    }
}

#[derive(Debug, Clone, Copy)]
pub struct IndividualTelemetry {
    /// Generation in which this individual was created
    pub birth_generation: Option<usize>,

    // Number of crossovers this individual was part of
    pub crossover_involvement: Option<usize>,
}

impl IndividualTelemetry {
    pub fn new() -> Self {
        Self {
            birth_generation: None,
            crossover_involvement: None,
        }
    }
}
