use axum::{
    http::HeaderValue,
    routing::{get, post},
    Router,
};
use tower_http::cors::{Any, CorsLayer};

use crate::{handler, ServerState};

pub fn create_router(server_state: ServerState) -> Router {
    Router::new()
        .route("/batches", get(handler::batches))
        .route("/table", get(handler::table))
        .route("/process", post(handler::process_batch))
        .layer(
            CorsLayer::new()
                .allow_origin("*".parse::<HeaderValue>().unwrap())
                .allow_headers(Any),
        )
        .with_state(server_state)
}
