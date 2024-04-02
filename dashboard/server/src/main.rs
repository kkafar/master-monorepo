use axum::{response::{Html, IntoResponse}, routing::get, Router};

async fn handler() -> impl IntoResponse {
    Html("<h1>Hello, World!</h1>")
}

#[tokio::main]
async fn main() {

    // build our application with a route
    let app = Router::new().route("/", get(handler));

    // run it
    let listener = tokio::net::TcpListener::bind("127.0.0.1:8088")
        .await
        .unwrap();
    println!("listening on {}", listener.local_addr().unwrap());
    axum::serve(listener, app).await.unwrap();
}
