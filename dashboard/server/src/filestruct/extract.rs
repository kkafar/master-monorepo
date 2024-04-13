use std::io::BufReader;

use crate::data::model::batch::BatchConfigModel;

use super::model::raw::BatchConfigFile;


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
