pub mod messages;
pub mod processed;
pub mod raw;

pub use raw::{batch, experiment, problem, series};

use crate::{config::Config, ecdk::proxy::EcdkProxy};

#[derive(Debug, Clone)]
pub struct ServerState {
    pub cfg: Config,
    pub ecdk_proxy: EcdkProxy,
}
