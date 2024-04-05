use axum::{http::HeaderValue, routing::{get, Route}, Router};
use tower_http::cors::CorsLayer;

use crate::{handler, ServerState};


pub fn create_router(server_state: ServerState) -> Router {
    let router = Router::new()
        .route("/batches", get(handler::batches))
        .layer(CorsLayer::new().allow_origin("*".parse::<HeaderValue>().unwrap()))
        .with_state(server_state);

    return router;
}
