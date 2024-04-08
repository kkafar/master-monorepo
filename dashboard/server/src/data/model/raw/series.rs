///! Definitions of series level structures
use serde::Serialize;

#[derive(Serialize, Debug, Clone)]
pub struct RunMetadataFileData {
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
