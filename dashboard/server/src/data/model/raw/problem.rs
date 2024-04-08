///! Definitions of problem model structures

use serde::Serialize;

#[derive(Serialize, Debug, Clone)]
pub struct InstanceInfo {
    pub id: String,

    #[serde(rename = "ref")]
    pub reference: String,
    pub jobs: usize,
    pub machines: usize,
    pub lower_bound: usize,
    pub lower_bound_ref: String,
    pub best_solution: usize,
    pub best_solution_ref: String,
    pub best_solution_time: String,
    pub best_solution_time_ref: String,
}
