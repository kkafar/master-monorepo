///! Definitions of series level structures

use std::collections::HashMap;
use serde::Serialize;
use polars::prelude::*;

#[derive(Serialize, Debug, Clone)]
pub struct RunMetadataFileModel {
    pub solution_string: String,
    pub hash: String,
    pub fitness: usize,
    pub generation_count: usize,
    pub total_time: usize,
    pub chromosome: Vec<f64>,

    pub avg_age: Option<f64>,
    pub age_max: Option<usize>,
    pub individual_count: Option<usize>,
    pub crossover_involvement_max: Option<usize>,
    pub crossover_involvement_min: Option<usize>,
    pub start_timestamp: String,
    pub end_timestamp: String,
}


pub struct LazyDataFrameStore {
}

pub struct SeriesDataModel {
    pub run_metadata: RunMetadataFileModel,
    event_data: HashMap<String, DataFrame>,
}

pub mod event {
    pub const BEST_IN_GEN: &str = "bestingen";
    pub const ITER_INFO: &str = "iterinfo";
    pub const NEW_BEST: &str = "newbest";
    pub const POP_GEN_TIME: &str = "popgentime";
    pub const POP_METRICS: &str = "popmetrics";
}
