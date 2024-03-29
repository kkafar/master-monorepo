use super::RunConfig;
use serde::Serialize;


#[derive(Clone, Serialize)]
pub struct SolverDescription {
    codename: String,
    run_cfg: RunConfig,
    description: String,
}

impl SolverDescription {
    pub fn new(codename: String, run_cfg: RunConfig, description: String) -> Self {
        Self {
            codename,
            run_cfg,
            description,
        }
    }

    pub fn to_json(&self) -> String {
        serde_json::to_string_pretty(&self).unwrap()
    }
}

