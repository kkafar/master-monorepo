pub mod cli;
pub mod config;

pub use clap::Parser;

use axum::{extract::State, http::{HeaderValue, StatusCode}, response::{Html, IntoResponse, Response}, routing::get, Json, Router};
use serde;
use tower_http::{self, cors::CorsLayer};

use crate::config::Config;

#[derive(Debug, Clone)]
struct ServerState {
    cfg: Config,
}

#[derive(serde::Serialize)]
struct BatchesResponse {
    #[serde(rename = "batchNames")]
    batch_names: Vec<String>,
}

async fn handler() -> Response {
    Html("<h1>Hello, World!</h1>").into_response()
}

async fn batches(State(state): State<ServerState>) -> Response {
    let batches = state.cfg.results_dir
        .read_dir()
        .unwrap()
        .filter_map(|file| file.ok())
        .filter_map(|file| file.path().file_stem().unwrap().to_os_string().into_string().ok())
        .collect::<Vec<String>>();

    println!("{:?}", batches);

    (StatusCode::OK, Json(BatchesResponse{batch_names: batches})).into_response()
}


#[tokio::main]
async fn main() {
    let args: cli::Args = cli::Args::parse();
    let cfg = Config::try_from_args(&args).expect("Failed to create server config!");

    // build our application with a route
    let app = Router::new()
        .route("/", get(handler))
        .route("/batches", get(batches))
        .layer(CorsLayer::new().allow_origin("*".parse::<HeaderValue>().unwrap()))
        .with_state(ServerState{cfg: cfg.clone()});

    // run it
    let listener = tokio::net::TcpListener::bind(format!("127.0.0.1:{}", cfg.port))
        .await
        .unwrap();
    println!("listening on {}", listener.local_addr().unwrap());
    axum::serve(listener, app).await.unwrap();
}
