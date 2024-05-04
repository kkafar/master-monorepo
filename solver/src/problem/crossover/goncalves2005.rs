use ecrs::{
    ga::{individual::IndividualTrait, Metrics},
    prelude::crossover::CrossoverOperator,
};
use rand::{thread_rng, Rng};

use crate::{problem::individual::JsspIndividual, stats::IndividualTelemetry};

pub struct Goncalves2005Crossover {
    distr: rand::distributions::Uniform<f64>,
}

impl Goncalves2005Crossover {
    pub fn new() -> Self {
        Self {
            distr: rand::distributions::Uniform::new(0.0, 1.0),
        }
    }

    fn apply_single(
        &mut self,
        metadata: &Metrics,
        parent_1: &JsspIndividual,
        parent_2: &JsspIndividual,
    ) -> JsspIndividual {
        let chromosome_len = parent_1.chromosome().len();

        parent_1.telemetry.on_crossover();
        parent_2.telemetry.on_crossover();

        let mut child_1_ch = <JsspIndividual as IndividualTrait>::ChromosomeT::default();

        let mask = thread_rng().sample_iter(self.distr).take(chromosome_len);

        for (locus, val) in mask.enumerate() {
            if val <= 0.7 {
                child_1_ch.push(parent_1.chromosome()[locus]);
            } else {
                child_1_ch.push(parent_2.chromosome()[locus]);
            }
        }

        let mut child_1 = parent_1.clone();

        child_1.is_fitness_valid = false;
        child_1.chromosome = child_1_ch;

        // We do not call `child_1.telemetry.on_create(metadata.generation)` because
        // we replace child's telemetry with a new object anyway.
        // TODO: Create separate method for cloning individual with right semantics.

        child_1.telemetry = IndividualTelemetry::new(metadata.generation, 0);
        child_1
    }
}

impl CrossoverOperator<JsspIndividual> for Goncalves2005Crossover {
    fn apply(&mut self, metadata: &Metrics, selected: &[&JsspIndividual]) -> Vec<JsspIndividual> {
        assert!(selected.len() & 1 == 0);

        let mut output = Vec::with_capacity(selected.len());

        for parents in selected.chunks(2) {
            let child_1 = self.apply_single(metadata, parents[0], parents[1]);
            output.push(child_1);
        }

        output
    }
}
