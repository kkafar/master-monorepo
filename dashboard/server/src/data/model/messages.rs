use serde;

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
