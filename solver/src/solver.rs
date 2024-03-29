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
    stats::{StatsAware, StatsEngine},
};

#[derive(Clone, Copy)]
pub struct RunConfig {
    pop_size: usize,
    n_gen: usize,

    /// Elitims rate passed to JsspCrossover operator in solvers that utilise it.
    /// See JsspCrossover implementation to understand its meaning exactly.
    elitism_rate: f64,

    /// Sampling rate passed to JsspCrossover operator in solvers that utilise it
    /// See JsspCrossover implementation to understand its meaning exactly.
    sampling_rate: f64,
}

pub fn get_run_config(instance: &JsspInstance, config: &Config) -> RunConfig {
    // TODO: Create single place with solver defaults, right now its here
    // and in config creation...

    // TODO: Do I really need this RunConfig structure? Maybe just pass config around

    RunConfig {
        pop_size: config.pop_size.unwrap_or(instance.cfg.n_ops * 2),
        n_gen: config.n_gen.unwrap_or(400),
        elitism_rate: config.elitism_rate,
        sampling_rate: config.sampling_rate,
    }
}

pub trait Solver {
    /// Run solver for given instance
    fn run(&mut self, instance: JsspInstance, run_config: RunConfig) -> anyhow::Result<()>;

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
    fn run(&mut self, instance: JsspInstance, run_config: RunConfig) -> anyhow::Result<()> {
        info!(
            "Running {} solver",
            self.describe().expect("No solver description provided")
        );

        let stats_engine = StatsEngine::new();
        let mut replacement_op = JsspReplacement::new(
            JsspPopProvider::new(instance.clone()),
            run_config.elitism_rate,
            run_config.sampling_rate,
        );
        replacement_op.set_stats_engine(&stats_engine);

        ga::Builder::new()
            .set_selection_operator(selection::Random::new())
            .set_crossover_operator(JsspCrossover::new())
            .set_mutation_operator(mutation::Identity::new())
            .set_population_generator(JsspPopProvider::new(instance))
            .set_replacement_operator(replacement_op)
            .set_fitness(JsspFitness::new(1.5))
            .set_probe(JsspProbe::new(&stats_engine))
            // .set_max_duration(std::time::Duration::from_secs(30))
            .set_max_generation_count(run_config.n_gen)
            .set_population_size(run_config.pop_size)
            .build()
            .run();

        anyhow::Ok(())
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
    fn run(&mut self, instance: JsspInstance, run_config: RunConfig) -> anyhow::Result<()> {
        info!(
            "Running {} solver",
            self.describe().expect("No solver description provided")
        );

        let stats_engine = StatsEngine::new();
        let mut replacement_op = ReplaceWithRandomPopulation::new(JsspPopProvider::new(instance.clone()));
        replacement_op.set_stats_engine(&stats_engine);

        ga::Builder::new()
            .set_population_generator(JsspPopProvider::new(instance))
            .set_fitness(JsspFitness::new(1.5))
            .set_selection_operator(EmptySelection::new())
            .set_crossover_operator(NoopCrossover::new())
            .set_mutation_operator(mutation::Identity::new())
            .set_replacement_operator(replacement_op)
            .set_probe(JsspProbe::new(&stats_engine))
            .set_max_generation_count(run_config.n_gen)
            .set_population_size(run_config.pop_size)
            .build()
            .run();

        anyhow::Ok(())
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
    fn run(&mut self, instance: JsspInstance, run_config: RunConfig) -> anyhow::Result<()> {
        info!(
            "Running {} solver",
            self.describe().expect("No solver description provided")
        );

        let stats_engine = StatsEngine::new();
        let mut replacement_op = JsspReplacement::new(JsspPopProvider::new(instance.clone()), 0.1, 0.2);
        replacement_op.set_stats_engine(&stats_engine);

        ga::Builder::new()
            .set_selection_operator(selection::Random::new())
            .set_crossover_operator(MidPoint::new())
            .set_mutation_operator(mutation::Identity::new())
            .set_population_generator(JsspPopProvider::new(instance))
            .set_replacement_operator(replacement_op)
            .set_fitness(JsspFitness::new(1.5))
            .set_probe(JsspProbe::new(&stats_engine))
            // .set_max_duration(std::time::Duration::from_secs(30))
            .set_max_generation_count(run_config.n_gen)
            .set_population_size(run_config.pop_size)
            .build()
            .run();

        anyhow::Ok(())
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
    fn run(&mut self, instance: JsspInstance, run_config: RunConfig) -> anyhow::Result<()> {
        info!(
            "Running {} solver",
            self.describe().expect("No solver description provided")
        );

        let stats_engine = StatsEngine::new();
        let mut replacement_op = JsspReplacement::new(JsspPopProvider::new(instance.clone()), 0.1, 0.2);
        replacement_op.set_stats_engine(&stats_engine);

        ga::Builder::new()
            .set_selection_operator(selection::Random::new())
            .set_crossover_operator(DoubledCrossover::new(instance.cfg.n_ops * 2))
            .set_mutation_operator(mutation::Identity::new())
            .set_population_generator(JsspPopProvider::new(instance))
            .set_replacement_operator(replacement_op)
            .set_fitness(JsspFitness::new(1.5))
            .set_probe(JsspProbe::new(&stats_engine))
            // .set_max_duration(std::time::Duration::from_secs(30))
            .set_max_generation_count(run_config.n_gen)
            .set_population_size(run_config.pop_size)
            .build()
            .run();

        anyhow::Ok(())
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
