use std::collections::HashMap;

use super::Solver;

pub struct SolverRegistry(pub HashMap<String, Box<dyn Solver>>);

impl SolverRegistry {
    pub fn new() -> Self {
        SolverRegistry(HashMap::new())
    }

    pub fn insert(&mut self, solver: Box<dyn Solver>) {
        self.0.insert(solver.codename(), solver);
    }

    #[allow(dead_code)]
    pub fn insert_with_name(&mut self, name: impl Into<String>, solver: Box<dyn Solver>) {
        self.0.insert(name.into(), solver);
    }

    #[allow(dead_code)]
    pub fn remove(&mut self, name: impl Into<String>) {
        self.0.remove(&name.into());
    }

    pub fn get(&mut self, name: impl Into<String>) -> Option<&mut Box<dyn Solver>> {
        self.0.get_mut(&name.into())
    }
}
