pub mod messages;
pub mod raw;

pub use raw::{batch, experiment, problem, series};

use crate::config::Config;

#[derive(Debug, Clone)]
pub struct ServerState {
    pub cfg: Config,
}
