use serde;

use super::batch::BatchConfigModel;

#[derive(serde::Serialize)]
pub struct BatchInfo {
    pub name: String,

    // #[serde(rename(serialize = "solvedCount"))]
    // pub solved_count: usize,

    pub config: BatchConfigModel,
}

#[derive(serde::Serialize)]
pub struct BatchesResponse {
    #[serde(rename = "batchInfo")]
    pub batch_info: Vec<BatchInfo>,
}
