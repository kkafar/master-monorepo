use std::path::PathBuf;

pub struct SeriesDir {
    pub path: PathBuf,
    pub bestingen_file: PathBuf,
    pub iterinfo_file: PathBuf,
    pub newbest_file: PathBuf,
    pub popgentime_file: PathBuf,
    pub popmetrics_file: PathBuf,
    pub run_metadata_file: PathBuf,
    pub stdout_file: PathBuf,
}

pub struct ExperimentDir {
    pub path: PathBuf,
    pub series_dirs: Vec<SeriesDir>,
}

pub struct BatchConfigFile {
    pub path: PathBuf,
}

pub struct BatchDir {
    pub path: PathBuf,
    pub config_file: BatchConfigFile,
    pub experiment_dirs: Vec<ExperimentDir>,
}

pub struct BatchCollectionDir {
    pub path: PathBuf,
    pub batch_dirs: Vec<BatchDir>,
}

impl BatchCollectionDir {
    pub fn try_from_dir(dir: impl Into<PathBuf>) -> anyhow::Result<Self> {
        let dir: PathBuf = dir.into();

        if !dir.is_dir() {
            anyhow::bail!("Provided path: {:?} is not a directory", dir);
        }

        let batch_dirs = dir
            .read_dir()?
            .filter_map(|entry| entry.ok())
            .filter_map(|entry| BatchDir::try_from_dir(entry.path()).ok())
            .collect::<Vec<BatchDir>>();

        Ok(Self {
            path: dir,
            batch_dirs,
        })
    }
}

impl BatchDir {
    pub fn batch_name(&self) -> &str {
        return self.path.file_stem().unwrap().to_str().unwrap();
    }

    pub fn try_from_dir(dir: impl Into<PathBuf>) -> anyhow::Result<Self> {
        let dir: PathBuf = dir.into();

        if !dir.is_dir() {
            anyhow::bail!("Provided path: {:?} is not a directory", dir);
        }

        let config_path = dir.join("config.json");

        if !config_path.is_file() {
            anyhow::bail!("Failed to find batch config at: {:?}", config_path);
        }

        let experiment_dirs = dir
            .read_dir()?
            .filter_map(|entry| entry.ok())
            .filter(|entry| match entry.file_type() {
                Ok(ft) => ft.is_dir(),
                Err(_) => false,
            })
            .filter_map(|entry| ExperimentDir::try_from_dir(entry.path()).ok())
            .collect::<Vec<ExperimentDir>>();

        Ok(Self {
            path: dir,
            config_file: BatchConfigFile::try_from_file(config_path)?,
            experiment_dirs,
        })
    }
}

impl BatchConfigFile {
    pub fn try_from_file(file: impl Into<PathBuf>) -> anyhow::Result<Self> {
        let file: PathBuf = file.into();

        if !file.is_file() {
            anyhow::bail!("Provided path: {:?} is not a file", file);
        }

        Ok(Self { path: file })
    }
}

impl ExperimentDir {
    pub fn try_from_dir(dir: impl Into<PathBuf>) -> anyhow::Result<Self> {
        let dir: PathBuf = dir.into();

        if !dir.is_dir() {
            anyhow::bail!("Provided path: {:?} is not a directory", dir);
        }

        Ok(Self {
            path: dir,
            series_dirs: Vec::new(),
        })
    }
}

impl SeriesDir {
    pub fn try_from_dir(_dir: impl Into<PathBuf>) -> anyhow::Result<Self> {
        todo!()
    }
}
