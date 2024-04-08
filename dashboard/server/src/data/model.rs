pub mod raw;
pub mod messages;

pub use raw::{batch, experiment, series, problem};

use crate::config::Config;

#[derive(Debug, Clone)]
pub struct ServerState {
    pub cfg: Config,
}


