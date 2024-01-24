#![allow(dead_code)]

use ecrs::{ga::individual::IndividualTrait, prelude::crossover::CrossoverOperator};
use rand::{thread_rng, Rng, rngs::ThreadRng};

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

        // We are using here problem trait, that chromosome_len is divisible by 2
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

pub struct DoubledCrossover {
    chromosome_len: usize,
    midpoint: usize,
    rng: ThreadRng,
    left_dist: rand::distributions::Uniform<usize>,
    right_dist: rand::distributions::Uniform<usize>,
}

impl DoubledCrossover {
    pub fn new(chromosome_len: usize) -> Self {
        // We are using here problem characteristic, that chromosome_len is divisible by 2
        let midpoint = chromosome_len / 2;
        Self {
            chromosome_len,
            midpoint,
            rng: rand::thread_rng(),
            left_dist: rand::distributions::Uniform::new(0, midpoint),
            right_dist: rand::distributions::Uniform::new(midpoint, chromosome_len),
        }
    }
}

impl CrossoverOperator<JsspIndividual> for DoubledCrossover {
    fn apply(&mut self, parent_1: &JsspIndividual, parent_2: &JsspIndividual) -> (JsspIndividual, JsspIndividual) {
        let mut child_1 = parent_1.clone();
        let mut child_2 = parent_2.clone();

        // It draws from the uniform distribution. It turns out that normal distribution for
        // integers is not supported. Need to work on that.
        let left_midpoint = self.rng.sample(self.left_dist);
        let right_midpoint = self.rng.sample(self.right_dist);


        // Already in place in this implementation
        // for i in 0..left_midpoint {
        //
        // }

        for i in left_midpoint..self.midpoint {
            child_1.chromosome[i] = parent_2.chromosome[i];
            child_2.chromosome[i] = parent_1.chromosome[i];
        }

        // Already in place in this implementation
        // for i in self.midpoint..right_midpoint {
        //
        // }

        for i in right_midpoint..self.chromosome_len {
            child_1.chromosome[i] = parent_2.chromosome[i];
            child_2.chromosome[i] = parent_1.chromosome[i];

        }

        child_1.is_fitness_valid = false;
        child_2.is_fitness_valid = false;

        (child_1, child_2)
    }
}


#[cfg(test)]
mod test {
    use ecrs::ga::{Individual, operators::crossover::CrossoverOperator};
    use itertools::Itertools;

    use crate::problem::{crossover::{MidPoint, DoubledCrossover}, individual::JsspIndividual};

    #[test]
    fn midpoint_works_as_expected() {
        let mut op = MidPoint::new();

        let parent_1_chromosome = vec![8.0, 4.0, 7.0, 3.0, 6.0, 2.0, 5.0, 1.0, 9.0, 0.0];
        let parent_2_chromosome = vec![0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0];

        let p1 = JsspIndividual::from(parent_1_chromosome.clone());
        let p2 = JsspIndividual::from(parent_2_chromosome.clone());

        let (child_1, child_2) = op.apply(&p1, &p2);

        let child_1_expected_chromosome = vec![8.0, 4.0, 7.0, 3.0, 6.0, 5.0, 6.0, 7.0, 8.0, 9.0];
        let child_2_expected_chromosome = vec![0.0, 1.0, 2.0, 3.0, 4.0, 2.0, 5.0, 1.0, 9.0, 0.0];

        assert_eq!(child_1.chromosome, child_1_expected_chromosome);
        assert_eq!(child_2.chromosome, child_2_expected_chromosome);
    }

    #[test]
    fn doubled_works_as_expected() {
        let parent_1_chromosome = vec![10.0, 11.0, 12.0, 13.0, 14.0, 15.0, 16.0, 17.0, 18.0, 19.0];
        let parent_2_chromosome = vec![0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0];
        let chromosome_len = parent_1_chromosome.len();
        let midpoint = chromosome_len / 2;

        let mut op = DoubledCrossover::new(parent_1_chromosome.len());

        let p1 = JsspIndividual::from(parent_1_chromosome.clone());
        let p2 = JsspIndividual::from(parent_2_chromosome.clone());

        let (child_1, child_2) = op.apply(&p1, &p2);
        println!("{parent_1_chromosome:?}\n{parent_2_chromosome:?}\n{:?}\n{:?}", &child_1.chromosome, &child_2.chromosome);

        let mut iter_1_1 = child_1.chromosome.iter().zip(parent_1_chromosome.iter());
        let mut iter_2_2 = child_2.chromosome.iter().zip(parent_2_chromosome.iter());
        let iter_1_2 = child_1.chromosome.iter().zip(parent_2_chromosome.iter());
        let iter_2_1 = child_2.chromosome.iter().zip(parent_1_chromosome.iter());

        // Imagine that both chromosomes are [1, 1, 1, ..., 1] -> this assertion method won't
        // hold. But in the case defined above it should work.
        let left_midpoint_1 = iter_1_1.find_position(|(&gene_a, &gene_b)| gene_a != gene_b);
        let left_midpoint_2 = iter_2_2.find_position(|(&gene_a, &gene_b)| gene_a != gene_b);

        assert!(left_midpoint_1.is_some());
        assert!(left_midpoint_2.is_some());

        let (left_midpoint_idx_1, _) = left_midpoint_1.unwrap();
        let (left_midpoint_idx_2, _) = left_midpoint_2.unwrap();

        assert!(left_midpoint_idx_1 < midpoint);
        assert!(left_midpoint_idx_2 < midpoint);
        assert_eq!(left_midpoint_idx_1, left_midpoint_idx_2);

        let mut iter_1_2 = iter_1_2.skip(left_midpoint_idx_1);
        let mut iter_2_1 = iter_2_1.skip(left_midpoint_idx_1);

        let left_midpoint_1 = iter_1_2.find_position(|(&gene_a, &gene_b)| gene_a == gene_b);
        let left_midpoint_2 = iter_2_1.find_position(|(&gene_a, &gene_b)| gene_a == gene_b);

        assert!(left_midpoint_1.is_some());
        assert!(left_midpoint_2.is_some());

        let (left_midpoint_idx_1, _) = left_midpoint_1.unwrap();
        let (left_midpoint_idx_2, _) = left_midpoint_2.unwrap();

        assert!(left_midpoint_idx_1 < midpoint);
        assert!(left_midpoint_idx_2 < midpoint);
        assert_eq!(left_midpoint_idx_1, left_midpoint_idx_2);

        let mut iter_1_1 = child_1.chromosome.iter().zip(parent_1_chromosome.iter()).skip(midpoint);
        let mut iter_2_2 = child_2.chromosome.iter().zip(parent_2_chromosome.iter()).skip(midpoint);
        let mut iter_1_2 = child_1.chromosome.iter().zip(parent_2_chromosome.iter()).skip(midpoint);
        let mut iter_2_1 = child_2.chromosome.iter().zip(parent_1_chromosome.iter()).skip(midpoint);

        let left_midpoint_1 = iter_1_1.find_position(|(&gene_a, &gene_b)| gene_a != gene_b);
        let left_midpoint_2 = iter_2_2.find_position(|(&gene_a, &gene_b)| gene_a != gene_b);

        assert!(left_midpoint_1.is_some());
        assert!(left_midpoint_2.is_some());

        let (left_midpoint_idx_1, _) = left_midpoint_1.unwrap();
        let (left_midpoint_idx_2, _) = left_midpoint_2.unwrap();

        assert!(left_midpoint_idx_1 < midpoint);
        assert!(left_midpoint_idx_2 < midpoint);
        assert_eq!(left_midpoint_idx_1, left_midpoint_idx_2);

        let mut iter_1_2 = iter_1_2.skip(left_midpoint_idx_1);
        let mut iter_2_1 = iter_2_1.skip(left_midpoint_idx_1);

        let left_midpoint_1 = iter_1_2.find_position(|(&gene_a, &gene_b)| gene_a == gene_b);
        let left_midpoint_2 = iter_2_1.find_position(|(&gene_a, &gene_b)| gene_a == gene_b);

        assert!(left_midpoint_1.is_some());
        assert!(left_midpoint_2.is_some());

        let (left_midpoint_idx_1, _) = left_midpoint_1.unwrap();
        let (left_midpoint_idx_2, _) = left_midpoint_2.unwrap();

        assert!(left_midpoint_idx_1 < midpoint);
        assert!(left_midpoint_idx_2 < midpoint);
        assert_eq!(left_midpoint_idx_1, left_midpoint_idx_2);
    }


}

