pub mod telemetry;

use ecrs::ga::GAMetadata;
pub use telemetry::IndividualTelemetry;

use std::{cell::RefCell, rc::Rc};

use crate::problem::individual::JsspIndividual;

#[derive(Clone, Copy)]
pub struct Stats {
    pub age_sum: usize,
    pub individual_count: usize,
    pub crossover_involvement_max: usize,
    pub crossover_involvement_min: usize,
    pub age_max: usize,
}

impl Stats {
    pub fn new(age_sum: usize, individual_count: usize) -> Self {
        Self {
            age_sum,
            individual_count,
            crossover_involvement_max: usize::MIN,
            crossover_involvement_min: usize::MAX,
            age_max: usize::MIN,
        }
    }

    pub fn update_stats_from_indvidual(&mut self, md: &GAMetadata, indv: &JsspIndividual) {
        let indv_age = md.generation - indv.telemetry.birth_generation();
        // assert!(
        //     indv_age > 0,
        //     "Individual can not be replaced in the same generation it was created. This happened in generation {indv_age}."
        // );

        self.age_sum += indv_age;
        self.age_max = self.age_max.max(indv_age);

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
    pub stats: Rc<RefCell<Stats>>,
}

impl StatsEngine {
    pub fn new() -> Self {
        Self {
            stats: Rc::new(RefCell::new(Stats::default())),
        }
    }

    #[allow(dead_code)]
    pub fn inner_owned(&self) -> Stats {
        self.stats.borrow().clone()
    }
}
