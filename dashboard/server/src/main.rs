pub mod cli;
pub mod config;
pub mod handler;
pub mod model;
pub mod routing;

use crate::{config::Config, model::ServerState};
pub use clap::Parser;

#[tokio::main]
async fn main() {
    let args: cli::Args = cli::Args::parse();
    let cfg = Config::try_from_args(&args).expect("Failed to create server config!");

    // build our application with a route
    let app = routing::create_router(ServerState { cfg: cfg.clone() });

    // run it
    let listener = tokio::net::TcpListener::bind(format!("127.0.0.1:{}", cfg.port))
        .await
        .unwrap();
    println!("listening on {}", listener.local_addr().unwrap());
    axum::serve(listener, app).await.unwrap();
}
