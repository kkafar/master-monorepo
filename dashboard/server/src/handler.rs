use axum::{
    extract::State,
    http::StatusCode,
    response::{Html, IntoResponse, Response},
    Json,
};
use crate::data::model::ServerState;


pub async fn handler() -> Response {
    Html("<h1>Hello, World!</h1>").into_response()
}

pub async fn batches(State(state): State<ServerState>) -> Response {
    let directory_iter = match state.cfg.results_dir.read_dir() {
        Ok(read_dir) => read_dir,
        Err(err) => {
            return (StatusCode::INTERNAL_SERVER_ERROR, err.to_string()).into_response();
        }
    };

    let batch_names = directory_iter
        .filter_map(|entry| entry.ok())
        .map(|entry| entry.path())
        .filter(|file| file.is_dir())
        .filter_map(|file| {
            file
                .file_stem()
                .unwrap()
                .to_os_string()
                .into_string()
                .ok()
        })
        .collect::<Vec<String>>();

    // (StatusCode::OK, Json(BatchesResponse { batch_names })).into_response()
    todo!()
}
