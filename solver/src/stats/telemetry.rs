use std::{cell::RefCell, rc::Rc};

use ecrs::ga::GAMetadata;

use crate::problem::individual::JsspIndividual;

#[derive(Debug, Clone, Copy)]
struct Inner {
    /// Generation in which this individual was created
    pub birth_generation: usize,

    // Number of crossovers this individual was part of
    pub crossover_involvement: usize,
}

#[derive(Debug, Clone)]
pub struct IndividualTelemetry {
    state: Rc<RefCell<Inner>>,
}

impl IndividualTelemetry {
    pub fn new(birth_generation: usize, crossover_involvement: usize) -> Self {
        Self {
            state: Rc::new(RefCell::new(Inner {
                birth_generation,
                crossover_involvement,
            })),
        }
    }

    pub fn dummy() -> Self {
        Self::new(0, 0)
    }

    pub fn on_crossover(&self) {
        self.state.borrow_mut().crossover_involvement += 1;
    }

    pub fn on_create(&self, generation: usize) {
        let mut state = self.state.borrow_mut();
        state.birth_generation = generation;
        state.crossover_involvement = 0;
    }

    pub fn birth_generation(&self) -> usize {
        self.state.borrow().birth_generation
    }

    pub fn crossover_involvement(&self) -> usize {
        self.state.borrow().crossover_involvement
    }
}
