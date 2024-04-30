use axum::{
    http::HeaderValue,
    routing::{get, post},
    Router,
};
use tower_http::cors::{Any, CorsLayer};
use tower_http::services::ServeDir;

use crate::{handler, ServerState};

pub fn create_router(server_state: ServerState) -> Router {
    let fspath = server_state.cfg.processed_results_dir.clone();
    println!("FS on: {fspath:?}");

    Router::new()
        .route("/batches", get(handler::batches))
        .route("/table", get(handler::table))
        .route("/process", post(handler::process_batch))
        .route("/plots", get(handler::plots))
        // Only files from cwd down can be served by the webserver, otherwise the framework
        // returns 404. I believe API is shaped in such way due to browser security restrictions.
        // Therefore the server **MUST** be run in ecdk directory to work properly.
        .nest_service("/assets", ServeDir::new("."))
        .layer(
            CorsLayer::new()
                .allow_origin("*".parse::<HeaderValue>().unwrap())
                .allow_headers(Any),
        )
        .with_state(server_state)
}
