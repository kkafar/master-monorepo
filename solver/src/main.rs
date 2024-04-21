mod cli;
mod config;
mod logging;
mod parse;
mod problem;
mod solver;
mod stats;
mod util;

use config::Config;
use solver::registry::SolverRegistry;
use solver::{Goncalves2005, Goncalves2005DoubleMidPoint, Goncalves2005DoubledRank, Goncalves2005MidPoint, RandomSearch, RunConfig};

use crate::problem::JsspInstance;
use crate::util::dump_solver_description;

fn register_solvers(registry: &mut SolverRegistry) {
    registry.insert(Box::new(Goncalves2005));
    registry.insert(Box::new(Goncalves2005MidPoint));
    registry.insert(Box::new(Goncalves2005DoubleMidPoint));
    registry.insert(Box::new(RandomSearch));
    registry.insert(Box::new(Goncalves2005DoubledRank));
}

fn run() -> anyhow::Result<()> {
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

    let run_config = RunConfig::new(&instance, &config);
    let solver = solver_registry.get(&config.solver_type).unwrap_or_else(|| {
        panic!(
            "Failed to find solver of type {} in registry",
            &config.solver_type
        )
    });

    dump_solver_description(solver.description(run_config.clone()).to_json());
    solver.run(instance, run_config)
}

fn main() -> anyhow::Result<()> {
    run()
}
