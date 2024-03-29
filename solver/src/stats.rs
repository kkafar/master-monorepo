pub mod telemetry;

use ecrs::ga::GAMetadata;
pub use telemetry::IndividualTelemetry;

use std::{rc::Rc, cell::RefCell};

use crate::problem::individual::JsspIndividual;



pub trait StatsAware<'stats> {
    fn set_stats_engine(&mut self, engine: &'stats StatsEngine);
}

pub struct Stats {
    pub age_sum: usize,
    pub individual_count: usize,
    pub crossover_involvement_max: usize,
    pub crossover_involvement_min: usize,
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

    pub fn update_stats_from_indvidual(&mut self, md: &GAMetadata, indv: &JsspIndividual) {
        self.age_sum += md.generation - indv.telemetry.birth_generation();
        self.individual_count += 1;
        let indv_crossover_involvement = indv.telemetry.crossover_involvement();
        self.crossover_involvement_min = self.crossover_involvement_min.min(indv_crossover_involvement);
        self.crossover_involvement_max = self.crossover_involvement_max.max(indv_crossover_involvement);
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

