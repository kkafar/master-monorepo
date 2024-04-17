use std::io::BufReader;

use crate::data::model::{batch::BatchConfigModel, processed::tables::names};

use super::model::{processed::TablesDir, raw::BatchConfigFile};
use polars::{
    frame::DataFrame,
    io::{csv::CsvReader, SerReader},
};

impl BatchConfigFile {
    pub fn load_data(&self) -> anyhow::Result<BatchConfigModel> {
        // println!("Loaded model from path: {:?}", &self.path);
        let file = std::fs::OpenOptions::new()
            .read(true)
            .write(false)
            .open(&self.path)?;
        let model = serde_json::from_reader(BufReader::new(file))?;

        // println!("Loaded model: {:?}", model);

        Ok(model)
        // Ok(serde_json::from_reader(BufReader::new(file))?)
    }
}

impl TablesDir {
    pub fn load_summary_total_table(&self) -> anyhow::Result<DataFrame> {
        Ok(CsvReader::from_path(&self.summary_total)?.finish()?)
    }

    pub fn load_summary_by_exp_table(&self) -> anyhow::Result<DataFrame> {
        Ok(CsvReader::from_path(&self.summary_by_exp)?.finish()?)
    }

    pub fn load_convergence_info_table(&self) -> anyhow::Result<DataFrame> {
        if let Some(ref path) = self.convergence_info {
            Ok(CsvReader::from_path(path)?.finish()?)
        } else {
            anyhow::bail!("Missing convergence info table");
        }
    }

    pub fn load_run_summary_stats_table(&self) -> anyhow::Result<DataFrame> {
        if let Some(ref path) = self.run_summary_stats {
            Ok(CsvReader::from_path(path)?.finish()?)
        } else {
            anyhow::bail!("Missing run summary stats table");
        }
    }

    pub fn load_table(&self, table_name: &str) -> anyhow::Result<DataFrame> {
        match table_name {
            names::SUMMARY_TOTAL => self.load_summary_total_table(),
            names::SUMMARY_BY_EXP => self.load_summary_by_exp_table(),
            names::CONVERGENCE_INFO => self.load_convergence_info_table(),
            names::RUN_SUMMARY_STATS => self.load_run_summary_stats_table(),
            _ => anyhow::bail!("Unsupported table: {table_name}"),
        }
    }
}
