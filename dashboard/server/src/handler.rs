use crate::data::{
    filestruct::BatchCollectionDir,
    model::{
        messages::{BatchInfo, BatchesResponse},
        ServerState,
    },
};
use axum::{
    extract::State,
    http::StatusCode,
    response::{Html, IntoResponse, Response},
    Json,
};

pub async fn handler() -> Response {
    Html("<h1>Hello, World!</h1>").into_response()
}

pub async fn batches(State(state): State<ServerState>) -> Response {
    let batch_collection_dir = match BatchCollectionDir::try_from_dir(state.cfg.results_dir) {
        Ok(dir) => dir,
        Err(err) => return (StatusCode::INTERNAL_SERVER_ERROR, err.to_string()).into_response(),
    };

    let batch_info = batch_collection_dir.batch_dirs.iter().map(|batch_dir| {
        (
            batch_dir
                .path
                .file_stem()
                .unwrap()
                .to_str()
                .unwrap()
                .to_owned(),
            batch_dir.config_file.load_data(),
        )
    });

    let maybe_error: Vec<String> = batch_info
        .clone()
        .filter(|(_name, config_res)| config_res.is_err())
        .take(1)
        .map(|(_name, config_res)| config_res.unwrap_err().to_string())
        .collect();

    if !maybe_error.is_empty() {
        println!("Errors {:?}", maybe_error);
        return (
            StatusCode::INTERNAL_SERVER_ERROR,
            maybe_error.first().unwrap().to_owned(),
        )
            .into_response();
    }

    let batch_info = batch_collection_dir
        .batch_dirs
        .iter()
        .map(|batchdir| BatchInfo {
            name: batchdir
                .path
                .file_stem()
                .unwrap()
                .to_str()
                .unwrap()
                .to_owned(),
            config: batchdir.config_file.load_data().unwrap(),
        })
        .collect();

    (StatusCode::OK, Json(BatchesResponse { batch_info })).into_response()
}
