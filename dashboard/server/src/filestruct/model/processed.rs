use std::path::{Path, PathBuf};

pub struct ExperimentPlotDir {
    pub best_run_fit_plot: PathBuf,
    pub best_run_fit_avg_compound_plot: Option<PathBuf>,
    pub fitness_avg_plot: PathBuf,
    pub pop_met_plot: PathBuf,
    pub best_solution_plot: Option<PathBuf>,
}

pub struct PlotsDir {
    pub path: PathBuf,
    pub experiments_plot_dirs: Vec<ExperimentPlotDir>,
}

pub struct TablesDir {
    pub path: PathBuf,
    pub convergence_info: Option<PathBuf>,
    pub run_summary_stats: Option<PathBuf>,
    pub solutions: Option<PathBuf>,
    pub summary_by_exp: PathBuf,
    pub summary_total: PathBuf,
}

pub struct PBatchDir {
    pub path: PathBuf,
    pub plots_dir: PlotsDir,
    pub tables_dir: TablesDir,
    pub solver_desc_file: Option<PathBuf>,
}

pub struct PBatchCollectionDir {
    pub path: PathBuf,
    pub batch_dirs: Vec<PBatchDir>,
}

impl PBatchCollectionDir {
    pub fn try_from_dir(dir: impl Into<PathBuf>) -> anyhow::Result<Self> {
        let dir: PathBuf = dir.into();

        if !dir.is_dir() {
            anyhow::bail!("Provided path: {:?} is not a directory", dir);
        }

        let batch_dirs = dir
            .read_dir()?
            .filter_map(|entry| entry.ok())
            .filter_map(|entry| PBatchDir::try_from_dir(entry.path()).ok())
            .collect::<Vec<PBatchDir>>();

        Ok(Self {
            path: dir,
            batch_dirs,
        })
    }
}

impl PBatchDir {
    pub fn batch_name(&self) -> &str {
        return self.path.file_stem().unwrap().to_str().unwrap();
    }
    pub fn try_from_dir(dir: impl Into<PathBuf>) -> anyhow::Result<Self> {
        let dir: PathBuf = dir.into();

        if !dir.is_dir() {
            anyhow::bail!("Provided path: {:?} is not a directory", dir);
        }

        let plots_dir = dir.join("plots");
        let plots_dir = match PlotsDir::try_from_dir(plots_dir) {
            Ok(res) => res,
            Err(err) => anyhow::bail!("{:?}", err),
        };

        let tables_dir = dir.join("tables");
        let tables_dir = match TablesDir::try_from_dir(tables_dir) {
            Ok(res) => res,
            Err(err) => anyhow::bail!("{:?}", err),
        };

        let solver_desc_file = dir.join("solver_desc.json");
        let solver_desc_file = if solver_desc_file.is_file() {
            Some(solver_desc_file)
        } else {
            None
        };

        Ok(Self {
            path: dir,
            plots_dir,
            tables_dir,
            solver_desc_file,
        })
    }
}

impl PlotsDir {
    pub fn try_from_dir(dir: impl Into<PathBuf>) -> anyhow::Result<Self> {
        let dir: PathBuf = dir.into();
        if !dir.is_dir() {
            anyhow::bail!("Missing plots directory: {:?}", dir);
        }

        let experiments_plot_dirs = dir
            .read_dir()?
            .filter_map(|entry| entry.ok())
            .filter_map(|entry| ExperimentPlotDir::try_from_dir(entry.path()).ok())
            .collect::<Vec<ExperimentPlotDir>>();

        Ok(Self {
            path: dir,
            experiments_plot_dirs,
        })
    }
}

impl TablesDir {
    pub fn try_from_dir(dir: impl Into<PathBuf>) -> anyhow::Result<Self> {
        let dir: PathBuf = dir.into();
        if !dir.is_dir() {
            anyhow::bail!("Missing tables directory: {:?}", dir);
        }

        let summary_by_exp = dir.join("summary_by_exp.csv");
        if !summary_by_exp.is_file() {
            anyhow::bail!("Expected {:?} file to exist", summary_by_exp);
        }

        let summary_total = dir.join("summary_total.csv");
        if !summary_total.is_file() {
            anyhow::bail!("Expected {:?} file to exist", summary_total);
        }

        let convergence_info = dir.join("convergence_info.csv");
        let convergence_info = if convergence_info.is_file() {
            Some(convergence_info)
        } else {
            None
        };

        let run_summary_stats = dir.join("run_summary_stats.csv");
        let run_summary_stats = if run_summary_stats.is_file() {
            Some(run_summary_stats)
        } else {
            None
        };

        let solutions = dir.join("solutions.csv");
        let solutions = if solutions.is_file() {
            Some(solutions)
        } else {
            None
        };

        Ok(Self {
            path: dir,
            convergence_info,
            run_summary_stats,
            solutions,
            summary_by_exp,
            summary_total,
        })
    }
}

impl ExperimentPlotDir {
    pub fn try_from_dir(dir: impl Into<PathBuf>) -> anyhow::Result<Self> {
        let dir: PathBuf = dir.into();
        if !dir.is_dir() {
            anyhow::bail!("Missing tables directory: {:?}", dir);
        }

        let expname = Self::experiment_name(&dir);
        let best_run_fit_plot = dir.join(format!("{expname}_best_run_fit.png"));
        if !best_run_fit_plot.is_file() {
            anyhow::bail!("Missing plot: {:?}", best_run_fit_plot);
        }

        let fitness_avg_plot = dir.join(format!("{expname}_fit_avg.png"));
        if !fitness_avg_plot.is_file() {
            anyhow::bail!("Missing plot: {:?}", fitness_avg_plot);
        }

        let pop_met_plot = dir.join(format!("{expname}_pop_met.png"));
        if !pop_met_plot.is_file() {
            anyhow::bail!("Missing plot: {:?}", pop_met_plot);
        }

        let best_run_fit_avg_compound_plot =
            dir.join(format!("{expname}_best_run_fit_avg_compound.png"));
        let best_run_fit_avg_compound_plot = if best_run_fit_avg_compound_plot.is_file() {
            Some(best_run_fit_avg_compound_plot)
        } else {
            None
        };

        Ok(Self {
            best_run_fit_plot,
            best_run_fit_avg_compound_plot,
            fitness_avg_plot,
            pop_met_plot,
            best_solution_plot: None,
        })
    }

    fn experiment_name<'a>(dir: &'a Path) -> &'a str {
        dir.file_name().unwrap().to_str().unwrap()
    }
}
