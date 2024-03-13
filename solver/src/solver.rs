pub mod registry;

use ecrs::ga::{
    self,
    operators::{mutation, selection},
};
use log::info;

use crate::{
    config::{
        Config, SOLVER_TYPE_DEFAULT, SOLVER_TYPE_DOUBLED_CROSSOVER, SOLVER_TYPE_MIDPOINT,
        SOLVER_TYPE_RANDOMSEARCH,
    },
    problem::{
        crossover::{DoubledCrossover, JsspCrossover, MidPoint, NoopCrossover},
        fitness::JsspFitness,
        population::JsspPopProvider,
        probe::JsspProbe,
        replacement::{JsspReplacement, ReplaceWithRandomPopulation},
        selection::EmptySelection,
        JsspInstance,
    },
};

#[derive(Clone, Copy)]
pub struct RunConfig {
    pop_size: usize,
    n_gen: usize,
}

pub fn get_run_config(instance: &JsspInstance, config: &Config) -> RunConfig {
    let pop_size = if let Some(ps) = config.pop_size {
        ps // Overrided by user
    } else {
        instance.cfg.n_ops * 2 // Defined in paper
    };

    let n_gen = if let Some(ng) = config.n_gen {
        ng // Overrided by user
    } else {
        400 // Defined in paper
    };

    RunConfig { pop_size, n_gen }
}

pub trait Solver {
    /// Run solver for given instance
    fn run(&mut self, instance: JsspInstance, run_config: RunConfig);

    /// Return short description of the solver, e.g. mentioning the paper that the implementation
    /// bases on or simply solver name. Default Implementation returns None.
    fn describe(&self) -> Option<String> {
        None
    }

    /// Return codename of this solver. This is used by CLI to indicate which solver should be run.
    fn codename(&self) -> String;
}

pub struct Goncalves2005;

impl Solver for Goncalves2005 {
    fn run(&mut self, instance: JsspInstance, run_config: RunConfig) {
        info!(
            "Running {} solver",
            self.describe().expect("No solver description provided")
        );

        ga::Builder::new()
            .set_selection_operator(selection::Rank::new())
            .set_crossover_operator(JsspCrossover::new())
            .set_mutation_operator(mutation::Identity::new())
            .set_population_generator(JsspPopProvider::new(instance.clone()))
            .set_replacement_operator(JsspReplacement::new(JsspPopProvider::new(instance), 0.1, 0.2))
            .set_fitness(JsspFitness::new(1.5))
            .set_probe(JsspProbe::new())
            // .set_max_duration(std::time::Duration::from_secs(30))
            .set_max_generation_count(run_config.n_gen)
            .set_population_size(run_config.pop_size)
            .build()
            .run();
    }

    fn describe(&self) -> Option<String> {
        Some("Goncalves2005".into())
    }

    fn codename(&self) -> String {
        SOLVER_TYPE_DEFAULT.into()
    }
}

pub struct RandomSearch;

impl Solver for RandomSearch {
    fn run(&mut self, instance: JsspInstance, run_config: RunConfig) {
        info!(
            "Running {} solver",
            self.describe().expect("No solver description provided")
        );

        ga::Builder::new()
            .set_population_generator(JsspPopProvider::new(instance.clone()))
            .set_fitness(JsspFitness::new(1.5))
            .set_selection_operator(EmptySelection::new())
            .set_crossover_operator(NoopCrossover::new())
            .set_mutation_operator(mutation::Identity::new())
            .set_replacement_operator(ReplaceWithRandomPopulation::new(JsspPopProvider::new(instance)))
            .set_probe(JsspProbe::new())
            .set_max_generation_count(run_config.n_gen)
            .set_population_size(run_config.pop_size)
            .build()
            .run();
    }

    fn describe(&self) -> Option<String> {
        Some("RandomSearch".into())
    }

    fn codename(&self) -> String {
        SOLVER_TYPE_RANDOMSEARCH.into()
    }
}

pub struct Goncalves2005MidPoint;

impl Solver for Goncalves2005MidPoint {
    fn run(&mut self, instance: JsspInstance, run_config: RunConfig) {
        info!(
            "Running {} solver",
            self.describe().expect("No solver description provided")
        );

        ga::Builder::new()
            .set_selection_operator(selection::Rank::new())
            .set_crossover_operator(MidPoint::new())
            .set_mutation_operator(mutation::Identity::new())
            .set_population_generator(JsspPopProvider::new(instance.clone()))
            .set_replacement_operator(JsspReplacement::new(JsspPopProvider::new(instance), 0.1, 0.2))
            .set_fitness(JsspFitness::new(1.5))
            .set_probe(JsspProbe::new())
            // .set_max_duration(std::time::Duration::from_secs(30))
            .set_max_generation_count(run_config.n_gen)
            .set_population_size(run_config.pop_size)
            .build()
            .run();
    }

    fn describe(&self) -> Option<String> {
        Some("Goncalves2005 with MidPoint crossover operator".into())
    }

    fn codename(&self) -> String {
        SOLVER_TYPE_MIDPOINT.into()
    }
}

pub struct Goncalves2005DoubleMidPoint;

impl Solver for Goncalves2005DoubleMidPoint {
    fn run(&mut self, instance: JsspInstance, run_config: RunConfig) {
        info!(
            "Running {} solver",
            self.describe().expect("No solver description provided")
        );

        ga::Builder::new()
            .set_selection_operator(selection::Rank::new())
            .set_crossover_operator(DoubledCrossover::new(instance.cfg.n_ops * 2))
            .set_mutation_operator(mutation::Identity::new())
            .set_population_generator(JsspPopProvider::new(instance.clone()))
            .set_replacement_operator(JsspReplacement::new(JsspPopProvider::new(instance), 0.1, 0.2))
            .set_fitness(JsspFitness::new(1.5))
            .set_probe(JsspProbe::new())
            // .set_max_duration(std::time::Duration::from_secs(30))
            .set_max_generation_count(run_config.n_gen)
            .set_population_size(run_config.pop_size)
            .build()
            .run();
    }

    fn describe(&self) -> Option<String> {
        Some(
            "Goncalves2005 with Doubled crossover operator (midpoint on both halves of chromosome)"
                .to_string(),
        )
    }

    fn codename(&self) -> String {
        SOLVER_TYPE_DOUBLED_CROSSOVER.into()
    }
}
