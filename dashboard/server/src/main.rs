pub mod cli;
pub mod config;

pub use clap::Parser;

use axum::{response::{Html, IntoResponse, Response}, routing::get, Router};

async fn handler() -> Response {
    Html("<h1>Hello, World!</h1>").into_response()
}

#[tokio::main]
async fn main() {
    let args: cli::Args = cli::Args::parse();

    // build our application with a route
    let app = Router::new().route("/", get(handler));

    // run it
    let listener = tokio::net::TcpListener::bind("127.0.0.1:8088")
        .await
        .unwrap();
    println!("listening on {}", listener.local_addr().unwrap());
    axum::serve(listener, app).await.unwrap();
}
