use ecrs::{
    ga::Metrics,
    prelude::{population::PopulationGenerator, replacement::ReplacementOperator},
};

use crate::stats::StatsEngine;

use super::{individual::JsspIndividual, population::JsspPopProvider};

pub struct JsspReplacement<'stats> {
    pop_gen: JsspPopProvider,
    elite_rate: f64,
    sample_rate: f64,
    stats_engine: &'stats StatsEngine,
}

impl<'stats> JsspReplacement<'stats> {
    pub fn new(
        pop_gen: JsspPopProvider,
        elite_rate: f64,
        sample_rate: f64,
        stats_engine: &'stats StatsEngine,
    ) -> Self {
        Self {
            pop_gen,
            elite_rate,
            sample_rate,
            stats_engine,
        }
    }
}

impl<'stats> ReplacementOperator<JsspIndividual> for JsspReplacement<'stats> {
    fn apply(
        &mut self,
        metrics: &Metrics,
        mut population: Vec<JsspIndividual>,
        mut children: Vec<JsspIndividual>,
    ) -> Vec<JsspIndividual> {
        let elite_size: usize = (self.elite_rate * population.len() as f64) as usize;
        let sample_size: usize = (self.sample_rate * population.len() as f64) as usize;
        let crossover_size: usize = population.len() - elite_size - sample_size;

        assert!((0..population.len()).contains(&crossover_size));
        assert_eq!(elite_size + sample_size + crossover_size, population.len());

        if elite_size > 0 {
            population.sort();
        }

        let mut stats = self.stats_engine.stats.borrow_mut();

        // Divergence from the papaer here. They do sample children population randomly (or just
        // create just right amount of children).
        //
        // This implementation is biased, because children parents are selected from left-to-right
        // (thus from best to worst) and the offspring is put from left-to-right to the children
        // arrary & I'm copying here children from left to right ==> only children of better
        // individuals make it.
        //
        // Selection of parents is also done differently to the paper.
        for i in elite_size..(elite_size + crossover_size) {
            stats.update_stats_from_indvidual(metrics, &population[i]);
            std::mem::swap(&mut population[i], &mut children[i - elite_size]);
        }

        if sample_size > 0 {
            population
                .splice(
                    (elite_size + crossover_size)..population.len(),
                    self.pop_gen.generate_with_metadata(metrics, sample_size),
                )
                .for_each(|indv| stats.update_stats_from_indvidual(metrics, &indv))
        }

        population
    }

    fn requires_children_fitness(&self) -> bool {
        false
    }
}

pub struct ReplaceWithRandomPopulation<'stats> {
    pop_gen: JsspPopProvider,
    stats_engine: &'stats StatsEngine,
}

impl<'stats> ReplaceWithRandomPopulation<'stats> {
    pub fn new(pop_gen: JsspPopProvider, stats_engine: &'stats StatsEngine) -> Self {
        Self {
            pop_gen,
            stats_engine,
        }
    }
}

impl<'stats> ReplacementOperator<JsspIndividual> for ReplaceWithRandomPopulation<'stats> {
    fn apply(
        &mut self,
        _metrics: &Metrics,
        population: Vec<JsspIndividual>,
        _children: Vec<JsspIndividual>,
    ) -> Vec<JsspIndividual> {
        self.pop_gen.generate(population.len())
    }

    fn requires_children_fitness(&self) -> bool {
        false
    }
}
