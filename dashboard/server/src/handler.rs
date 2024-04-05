use axum::{
    extract::State,
    http::StatusCode,
    response::{Html, IntoResponse, Response},
    Json,
};
use serde;

use crate::ServerState;

#[derive(serde::Serialize)]
pub struct BatchesResponse {
    #[serde(rename = "batchNames")]
    pub batch_names: Vec<String>,
}

pub async fn handler() -> Response {
    Html("<h1>Hello, World!</h1>").into_response()
}

pub async fn batches(State(state): State<ServerState>) -> Response {
    let batches = state
        .cfg
        .results_dir
        .read_dir()
        .unwrap()
        .filter_map(|file| file.ok())
        .filter_map(|file| {
            file.path()
                .file_stem()
                .unwrap()
                .to_os_string()
                .into_string()
                .ok()
        })
        .collect::<Vec<String>>();

    println!("{:?}", batches);

    (
        StatusCode::OK,
        Json(BatchesResponse {
            batch_names: batches,
        }),
    )
        .into_response()
}
