use std::{path::PathBuf, str::FromStr};

#[derive(Clone, Debug)]
pub struct EcdkProxy {
    ecdk_dir: PathBuf,
    raw_dir: PathBuf,
    processed_dir: PathBuf,
}

impl EcdkProxy {
    pub fn new(ecdk_dir: PathBuf) -> Self {
        Self {
            ecdk_dir: ecdk_dir.clone(),
            raw_dir: ecdk_dir.join("raw.out"),
            processed_dir: ecdk_dir.join("processed.out"),
        }
    }

    pub async fn process(&self, batch_name: &str, max_cpus: usize) -> anyhow::Result<()> {
        let input_dir = PathBuf::from_str("raw.out").unwrap().join(batch_name);
        let output_dir = PathBuf::from_str("processed.out").unwrap().join(batch_name);

        let input_dir_str = input_dir.to_str().unwrap();
        let output_dir_str = output_dir.to_str().unwrap();

        let res = tokio::process::Command::new(".venv/bin/python")
            .arg("src/ecdk/main.py")
            .arg("analyze")
            .args(["--input-dir", input_dir_str])
            .args(["--output-dir", output_dir_str])
            .args(["--procs", max_cpus.to_string().as_str()])
            .arg("--plot")
            .current_dir(&self.ecdk_dir)
            .status()
            .await;

        match res {
            Ok(status) => {
                if let Some(code) = status.code() {
                    if code != 0 {
                        anyhow::bail!("Non zero status code {}", code)
                    } else {
                        Ok(())
                    }
                } else {
                    anyhow::bail!("No status code")
                }
            }
            Err(err) => anyhow::bail!("Error while executing process: {}", err),
        }
    }
}
