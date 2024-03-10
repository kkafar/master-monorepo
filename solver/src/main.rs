#![allow(unused_imports)]
mod cli;
mod config;
mod logging;
mod parse;
mod problem;
mod solver;
mod util;

use std::borrow::BorrowMut;
use std::path::{Path, PathBuf};
use std::time::Duration;

use cli::Args;
use config::{
    Config, SOLVER_TYPE_CUSTOM_CROSSOVER, SOLVER_TYPE_DEFAULT, SOLVER_TYPE_DOUBLED_CROSSOVER,
    SOLVER_TYPE_RANDOMSEARCH,
};
use ecrs::ga::probe::{AggregatedProbe, ElapsedTime, PolicyDrivenProbe, ProbingPolicy};
use ecrs::prelude::{crossover, ga, ops, replacement, selection};
use ecrs::{
    ga::{GAMetadata, Individual, StdoutProbe},
    prelude::{
        crossover::{CrossoverOperator, UniformParameterized},
        mutation::{self, Identity},
        replacement::{BothParents, ReplacementOperator},
        selection::{Rank, SelectionOperator},
    },
};
use log::info;
use problem::crossover::JsspCrossover;
use problem::fitness::JsspFitness;
use problem::individual::JsspIndividual;
use problem::population::JsspPopProvider;
use problem::probe::JsspProbe;
use problem::replacement::JsspReplacement;
use solver::registry::SolverRegistry;
use solver::{
    get_run_config, Goncalves2005, Goncalves2005DoubleMidPoint, Goncalves2005MidPoint, RandomSearch, Solver,
};

use crate::problem::crossover::{DoubledCrossover, MidPoint};
use crate::problem::{JsspConfig, JsspInstance};

fn register_solvers(registry: &mut SolverRegistry) {
    registry.insert(Box::new(Goncalves2005));
    registry.insert(Box::new(Goncalves2005MidPoint));
    registry.insert(Box::new(Goncalves2005DoubleMidPoint));
    registry.insert(Box::new(RandomSearch));
}

// fn get_default_solver() -> Box<dyn Solver> {
//     Box::new(Goncalves2005)
// }

fn run() {
    let args = cli::parse_args();
    let config = match Config::try_from(args) {
        Ok(config) => config,
        Err(err) => panic!("Failed to create config from args: {err}"),
    };

    util::assert_dir_exists(config.output_dir.as_ref());
    let event_map = util::create_event_map(config.output_dir.as_ref());

    if let Err(err) = logging::init_logging(&event_map, &config.output_dir.join("run_metadata.json")) {
        panic!("Logger initialization failed with error: {err}");
    }

    // Existance of input file is asserted during cli args parsing
    let instance = JsspInstance::try_from(&config.input_file).expect("Error while parsing instance file");

    let mut solver_registry = SolverRegistry::new();
    register_solvers(&mut solver_registry);

    let run_config = get_run_config(&instance, &config);
    let solver = solver_registry
        .get(&config.solver_type)
        .expect("Failed to find solver of given name");
    solver.run(instance, run_config);
}

fn main() -> Result<(), ()> {
    run();
    Ok(())
}
