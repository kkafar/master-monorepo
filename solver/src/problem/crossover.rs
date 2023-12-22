#![allow(dead_code)]

use ecrs::{ga::individual::IndividualTrait, prelude::crossover::CrossoverOperator};
use rand::{thread_rng, Rng};

use super::individual::JsspIndividual;

pub struct JsspCrossover {
    distr: rand::distributions::Uniform<f64>,
}

impl JsspCrossover {
    pub fn new() -> Self {
        Self {
            distr: rand::distributions::Uniform::new(0.0, 1.0),
        }
    }
}

impl CrossoverOperator<JsspIndividual> for JsspCrossover {
    fn apply(
        &mut self,
        parent_1: &JsspIndividual,
        parent_2: &JsspIndividual,
    ) -> (JsspIndividual, JsspIndividual) {
        let chromosome_len = parent_1.chromosome().len();

        let mut child_1_ch = <JsspIndividual as IndividualTrait>::ChromosomeT::default();
        let mut child_2_ch = <JsspIndividual as IndividualTrait>::ChromosomeT::default();

        let mask = thread_rng().sample_iter(self.distr).take(chromosome_len);

        for (locus, val) in mask.enumerate() {
            if val <= 0.6 {
                child_1_ch.push(parent_1.chromosome()[locus]);
                child_2_ch.push(parent_2.chromosome()[locus]);
            } else {
                child_1_ch.push(parent_2.chromosome()[locus]);
                child_2_ch.push(parent_1.chromosome()[locus]);
            }
        }

        let mut child_1 = parent_1.clone();
        let mut child_2 = parent_2.clone();
        child_1.is_fitness_valid = false;
        child_2.is_fitness_valid = false;
        child_1.chromosome = child_1_ch;
        child_2.chromosome = child_2_ch;

        (child_1, child_2)
    }
}

pub struct NoopCrossover;

impl NoopCrossover {
    pub fn new() -> Self {
        Self
    }
}

impl CrossoverOperator<JsspIndividual> for NoopCrossover {
    fn apply(
        &mut self,
        parent_1: &JsspIndividual,
        parent_2: &JsspIndividual,
    ) -> (JsspIndividual, JsspIndividual) {
        (parent_1.clone(), parent_2.clone())
    }
}

pub struct MidPoint;

impl MidPoint {
    pub fn new() -> Self {
        Self
    }
}

impl CrossoverOperator<JsspIndividual> for MidPoint {
    fn apply(&mut self, parent_1: &JsspIndividual, parent_2: &JsspIndividual) -> (JsspIndividual, JsspIndividual) {
        let mut child_1 = parent_1.clone();
        let mut child_2 = parent_2.clone();

        let chromosome_len = parent_1.chromosome.len();
        let midpoint = chromosome_len / 2;

        for i in midpoint..chromosome_len {
            child_1.chromosome[i] = parent_2.chromosome[i];
            child_2.chromosome[i] = parent_1.chromosome[i];
        }

        child_1.is_fitness_valid = false;
        child_2.is_fitness_valid = false;

        (child_1, child_2)
    }
}

