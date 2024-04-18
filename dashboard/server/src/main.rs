pub mod cli;
pub mod config;
pub mod data;
pub mod ecdk;
pub mod filestruct;
pub mod handler;
pub mod routing;

pub use clap::Parser;

use crate::{config::Config, data::model::ServerState, ecdk::proxy::EcdkProxy};

#[tokio::main]
async fn main() {
    let args: cli::Args = cli::Args::parse();
    let cfg = Config::try_from_args(&args).expect("Failed to create server config!");

    // build our application with a route
    let app = routing::create_router(ServerState {
        cfg: cfg.clone(),
        ecdk_proxy: EcdkProxy::new(cfg.ecdk_dir.clone()),
    });

    // run it
    let listener = tokio::net::TcpListener::bind(format!("127.0.0.1:{}", cfg.port))
        .await
        .unwrap();
    println!("listening on {}", listener.local_addr().unwrap());
    axum::serve(listener, app).await.unwrap();
}
