use serde;
use url::Url;

use super::batch::BatchConfigModel;

#[derive(serde::Serialize)]
pub struct BatchInfo {
    pub name: String,

    #[serde(rename(serialize = "solvedCount"))]
    pub solved_count: Option<usize>,

    pub config: BatchConfigModel,

    #[serde(rename(serialize = "isProcessed"))]
    pub is_processed: Option<bool>,
}

#[derive(serde::Serialize)]
pub struct BatchesResponse {
    #[serde(rename = "batchInfo")]
    pub batch_info: Vec<BatchInfo>,
}

#[derive(serde::Deserialize)]
pub struct TableRequest {
    #[serde(rename(deserialize = "batchName"))]
    pub batch_name: String,

    #[serde(rename(deserialize = "tableName"))]
    pub table_name: String,
}

#[derive(serde::Serialize)]
pub struct TableResponse {}

#[derive(serde::Deserialize)]
pub struct ProcessRequest {
    #[serde(rename(deserialize = "batchName"))]
    pub batch_name: String,

    #[serde(rename(deserialize = "maxCpus"))]
    pub max_cpus: Option<usize>,
}

#[derive(serde::Serialize)]
pub struct ProcessResponse {
    pub error: Option<String>,
}

impl ProcessResponse {
    pub fn new_err(message: String) -> Self {
        Self {
            error: Some(message),
        }
    }

    pub fn new_ok() -> Self {
        Self { error: None }
    }
}

#[derive(serde::Deserialize)]
pub struct BatchPlotsRequest {
    #[serde(rename(deserialize = "batchName"))]
    pub batch_name: String,
}

// export type ExperimentTables = {
//   bestRun: Url,
//   bestRunFitAvg?: Url,
//   fitAvg: Url,
//   popMet?: Url,
//   solution?: Url,
// }
#[derive(serde::Serialize)]
pub struct ExperimentPlotsPaths {
    #[serde(rename(serialize = "expName"))]
    pub exp_name: String,

    #[serde(rename(serialize = "bestRun"))]
    pub best_run_fit_plot: Url,

    #[serde(rename(serialize = "bestRunFitAvg"))]
    pub best_run_fit_avg_compound_plot: Option<Url>,

    #[serde(rename(serialize = "fitAvg"))]
    pub fitness_avg_plot: Url,

    #[serde(rename(serialize = "popMet"))]
    pub pop_met_plot: Url,

    #[serde(rename(serialize = "solution"))]
    pub best_solution_plot: Option<Url>,
}

#[derive(serde::Serialize)]
pub struct BatchPlotsResponse {
    #[serde(rename(serialize = "expPlots"))]
    pub exp_plots: Vec<ExperimentPlotsPaths>,
}
