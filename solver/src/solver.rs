pub mod description;
pub mod registry;
pub mod run_config;

pub use description::SolverDescription;
pub use run_config::RunConfig;

use ecrs::ga::{
    self,
    operators::{mutation, selection},
};
use log::info;

use crate::{
    config::{
        SOLVER_TYPE_DEFAULT, SOLVER_TYPE_DOUBLED_CROSSOVER, SOLVER_TYPE_MIDPOINT, SOLVER_TYPE_RANDOMSEARCH,
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

pub trait Solver {
    /// Run solver for given instance
    fn run(&mut self, instance: JsspInstance, run_config: RunConfig) -> anyhow::Result<()>;

    /// Returns short description of the solver, e.g. mentioning the paper that the implementation
    /// bases on or simply solver name.
    fn describe(&self) -> String;

    /// Returns codename of this solver. This is used by CLI to indicate which solver should be run.
    fn codename(&self) -> String;

    /// Returns structurized solver description which can be serialized & printed out
    fn description(&self, run_cfg: RunConfig) -> SolverDescription {
        SolverDescription::new(self.codename(), run_cfg, self.describe())
    }
}

pub struct Goncalves2005;

impl Solver for Goncalves2005 {
    fn run(&mut self, instance: JsspInstance, cfg: RunConfig) -> anyhow::Result<()> {
        info!("Running {} solver", self.describe());

        let stats_engine = StatsEngine::new();
        let mut replacement_op = JsspReplacement::new(
            JsspPopProvider::new(instance.clone()),
            cfg.elitism_rate,
            cfg.sampling_rate,
        );
        replacement_op.set_stats_engine(&stats_engine);

        ga::Builder::new()
            .set_selection_operator(selection::Random::new())
            .set_crossover_operator(JsspCrossover::new())
            .set_mutation_operator(mutation::Identity::new())
            .set_population_generator(JsspPopProvider::new(instance))
            .set_replacement_operator(replacement_op)
            .set_fitness(JsspFitness::new(cfg.delay_const_factor))
            .set_probe(JsspProbe::new(&stats_engine))
            // .set_max_duration(std::time::Duration::from_secs(30))
            .set_max_generation_count(cfg.n_gen)
            .set_population_size(cfg.pop_size)
            .build()
            .run();

        anyhow::Ok(())
    }

    fn describe(&self) -> String {
        "Goncalves2005 as defined in paper; random selection; jssp crossover (biased uniform) with 0.7 bias;
        no mutation; population sampled uniformly as random points; replacement with elitism & random sampling;
        fitness uses local search operator".into()
    }

    fn codename(&self) -> String {
        SOLVER_TYPE_DEFAULT.into()
    }
}

pub struct RandomSearch;

impl Solver for RandomSearch {
    fn run(&mut self, instance: JsspInstance, cfg: RunConfig) -> anyhow::Result<()> {
        info!("Running {} solver", self.describe());

        let stats_engine = StatsEngine::new();
        let mut replacement_op = ReplaceWithRandomPopulation::new(JsspPopProvider::new(instance.clone()));
        replacement_op.set_stats_engine(&stats_engine);

        ga::Builder::new()
            .set_population_generator(JsspPopProvider::new(instance))
            .set_fitness(JsspFitness::new(cfg.delay_const_factor))
            .set_selection_operator(EmptySelection::new())
            .set_crossover_operator(NoopCrossover::new())
            .set_mutation_operator(mutation::Identity::new())
            .set_replacement_operator(replacement_op)
            .set_probe(JsspProbe::new(&stats_engine))
            .set_max_generation_count(cfg.n_gen)
            .set_population_size(cfg.pop_size)
            .build()
            .run();

        anyhow::Ok(())
    }

    fn describe(&self) -> String {
        "RandomSearch; population sampled uniformly as random points; default fitness, USES LOCAL SEARCH OPERATOR;
        empty selection; noop crossover; no mutation; replacement operator replaces whole old population with newly sampled one".into()
    }

    fn codename(&self) -> String {
        SOLVER_TYPE_RANDOMSEARCH.into()
    }
}

pub struct Goncalves2005MidPoint;

impl Solver for Goncalves2005MidPoint {
    fn run(&mut self, instance: JsspInstance, cfg: RunConfig) -> anyhow::Result<()> {
        info!("Running {} solver", self.describe());

        let stats_engine = StatsEngine::new();
        let mut replacement_op = JsspReplacement::new(
            JsspPopProvider::new(instance.clone()),
            cfg.elitism_rate,
            cfg.sampling_rate,
        );
        replacement_op.set_stats_engine(&stats_engine);

        ga::Builder::new()
            .set_selection_operator(selection::Random::new())
            .set_crossover_operator(MidPoint::new())
            .set_mutation_operator(mutation::Identity::new())
            .set_population_generator(JsspPopProvider::new(instance))
            .set_replacement_operator(replacement_op)
            .set_fitness(JsspFitness::new(cfg.delay_const_factor))
            .set_probe(JsspProbe::new(&stats_engine))
            // .set_max_duration(std::time::Duration::from_secs(30))
            .set_max_generation_count(cfg.n_gen)
            .set_population_size(cfg.pop_size)
            .build()
            .run();

        anyhow::Ok(())
    }

    fn describe(&self) -> String {
        "Goncalves2005 with MidPoint crossover operator; random selection; no mutation; default population generation;
        default replacement with elitism and sampling new individuals; default fitness with local search operator".into()
    }

    fn codename(&self) -> String {
        SOLVER_TYPE_MIDPOINT.into()
    }
}

pub struct Goncalves2005DoubleMidPoint;

impl Solver for Goncalves2005DoubleMidPoint {
    fn run(&mut self, instance: JsspInstance, cfg: RunConfig) -> anyhow::Result<()> {
        info!("Running {} solver", self.describe());

        let stats_engine = StatsEngine::new();
        let mut replacement_op = JsspReplacement::new(
            JsspPopProvider::new(instance.clone()),
            cfg.elitism_rate,
            cfg.sampling_rate,
        );
        replacement_op.set_stats_engine(&stats_engine);

        ga::Builder::new()
            .set_selection_operator(selection::Random::new())
            .set_crossover_operator(DoubledCrossover::new(instance.cfg.n_ops * 2))
            .set_mutation_operator(mutation::Identity::new())
            .set_population_generator(JsspPopProvider::new(instance))
            .set_replacement_operator(replacement_op)
            .set_fitness(JsspFitness::new(cfg.delay_const_factor))
            .set_probe(JsspProbe::new(&stats_engine))
            // .set_max_duration(std::time::Duration::from_secs(30))
            .set_max_generation_count(cfg.n_gen)
            .set_population_size(cfg.pop_size)
            .build()
            .run();

        anyhow::Ok(())
    }

    fn describe(&self) -> String {
        "Goncalves2005 with Doubled crossover operator (singlepoint on both halves of chromosome);
        random selection; no mutation; default population provider (uniform points); default replacement with elitism and sampling rate;
        default fitness with local search operator".to_string()
    }

    fn codename(&self) -> String {
        SOLVER_TYPE_DOUBLED_CROSSOVER.into()
    }
}
