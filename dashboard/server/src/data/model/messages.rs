use serde;

use super::batch::BatchConfigModel;

#[derive(serde::Serialize)]
pub struct BatchInfo {
    pub name: String,
    pub config: BatchConfigModel,
}

#[derive(serde::Serialize)]
pub struct BatchesResponse {
    #[serde(rename = "batchInfo")]
    pub batch_info: Vec<BatchInfo>,
}
