mod cli;
mod config;
mod logging;
mod parse;
mod problem;
mod solver;
mod util;

use config::Config;
use solver::registry::SolverRegistry;
use solver::{
    get_run_config, Goncalves2005, Goncalves2005DoubleMidPoint, Goncalves2005MidPoint, RandomSearch,
};

use crate::problem::JsspInstance;

fn register_solvers(registry: &mut SolverRegistry) {
    registry.insert(Box::new(Goncalves2005));
    registry.insert(Box::new(Goncalves2005MidPoint));
    registry.insert(Box::new(Goncalves2005DoubleMidPoint));
    registry.insert(Box::new(RandomSearch));
}

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
