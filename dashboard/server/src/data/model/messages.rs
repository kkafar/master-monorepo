use serde;

use super::batch::BatchConfig;

#[derive(serde::Serialize)]
pub struct BatchesResponse {
    #[serde(rename = "batchConfigs")]
    pub batch_configs: Vec<BatchConfig>,
}

