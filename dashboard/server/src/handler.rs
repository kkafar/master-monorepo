use std::{collections::HashMap, io::BufWriter, path::PathBuf};

use crate::{
    data::model::{
        messages::{
            BatchInfo, BatchPlotsRequest, BatchPlotsResponse, BatchesResponse,
            ExperimentPlotsPaths, ProcessRequest, ProcessResponse, TableRequest,
        },
        ServerState,
    },
    filestruct::model::{
        processed::{ExperimentPlotDir, PBatchCollectionDir},
        raw::BatchCollectionDir,
    },
};

use anyhow::anyhow;
use axum::{
    extract::{Query, State},
    http::StatusCode,
    response::{IntoResponse, Response},
    Json,
};
use polars::{
    datatypes::AnyValue,
    frame::DataFrame,
    io::{json::JsonWriter, SerWriter},
};


fn path_to_url(path: &PathBuf, port: usize) -> anyhow::Result<url::Url> {
    // let path = path.canonicalize()?;
    let mut url = url::Url::parse("http://localhost")?;
    url.set_path(path.to_str().ok_or(anyhow!("Failed to convert path to str"))?);
    let _ = url.set_port(Some(port as u16));
    Ok(url)
}


pub async fn plots(
    State(state): State<ServerState>,
    request: Query<BatchPlotsRequest>,
) -> Response {
    println!("Process plots request");

    let batch_coll_dir = match PBatchCollectionDir::try_from_dir(state.cfg.processed_results_dir) {
        Ok(dir) => dir,
        Err(err) => {
            println!("Returning error {err}");
            return (StatusCode::INTERNAL_SERVER_ERROR, Json(err.to_string())).into_response();
        }
    };

    let batch_dir = match batch_coll_dir
        .batch_dirs
        .iter()
        .find(|&batch_dir| batch_dir.batch_name() == request.batch_name)
    {
        Some(batch_dir) => batch_dir,
        _ => {
            println!("Returning error Unable to find dir");
            return (
                StatusCode::BAD_REQUEST,
                Json("Unable to find directory for requested batch"),
            )
                .into_response();
        }
    };

    let results = batch_dir
        .plots_dir
        .experiments_plot_dirs
        .iter()
        .map(|plot_dir| {
            let port = state.cfg.port;
            let best_run_fit_plot = path_to_url(&plot_dir.best_run_fit_plot, port).unwrap();
            let best_run_fit_avg_compound_plot = if plot_dir.best_run_fit_avg_compound_plot.is_some() {
                Some(path_to_url(&plot_dir.best_run_fit_avg_compound_plot.clone().unwrap(), port).unwrap())
            } else {
                None
            };
            let fitness_avg_plot = path_to_url(&plot_dir.fitness_avg_plot, port).unwrap();
            let pop_met_plot = path_to_url(&plot_dir.pop_met_plot, port).unwrap();
            let best_solution_plot = if plot_dir.best_solution_plot.is_some() {
                Some(path_to_url(&plot_dir.best_solution_plot.clone().unwrap(), port).unwrap())
            } else {
                None
            };

            ExperimentPlotsPaths {
                exp_name: ExperimentPlotDir::experiment_name(&plot_dir.path).into(),
                best_run_fit_plot,
                best_run_fit_avg_compound_plot,
                fitness_avg_plot,
                pop_met_plot,
                best_solution_plot,
            }
        })
        .collect();

    println!("Success");
    (StatusCode::OK, Json(BatchPlotsResponse { exp_plots: results })).into_response()
}

pub async fn process_batch(
    State(state): State<ServerState>,
    Json(request): Json<ProcessRequest>,
) -> Response {
    println!("Process batch request");
    match state
        .ecdk_proxy
        .process(&request.batch_name, request.max_cpus.unwrap_or(8))
        .await
    {
        Err(err) => (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(ProcessResponse::new_err(err.to_string())),
        )
            .into_response(),
        _ => (StatusCode::OK, Json(ProcessResponse::new_ok())).into_response(),
    }
}

pub async fn table(State(state): State<ServerState>, request: Query<TableRequest>) -> Response {
    let batch_coll_dir = match PBatchCollectionDir::try_from_dir(state.cfg.processed_results_dir) {
        Ok(dir) => dir,
        Err(err) => {
            return (StatusCode::INTERNAL_SERVER_ERROR, Json(err.to_string())).into_response();
        }
    };

    let batch_dir = match batch_coll_dir
        .batch_dirs
        .iter()
        .find(|batch_dir| batch_dir.batch_name() == request.batch_name)
    {
        Some(dir) => dir,
        None => {
            return (
                StatusCode::BAD_REQUEST,
                Json(format!(
                    "Failed to find directory for batch of name: {}",
                    request.batch_name
                )),
            )
                .into_response();
        }
    };

    let mut table = match batch_dir.tables_dir.load_table(request.table_name.as_ref()) {
        Ok(df) => df,
        Err(err) => {
            return (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(format!(
                    "Failed to load table with name {} with error: {}",
                    request.table_name, err
                )),
            )
                .into_response();
        }
    };

    let mut buffer = Vec::<u8>::new();
    let mut writer = BufWriter::new(&mut buffer);

    JsonWriter::new(&mut writer)
        .with_json_format(polars::io::json::JsonFormat::Json)
        .finish(&mut table)
        .unwrap();

    std::mem::drop(writer);
    let table_as_string = String::from_utf8(buffer).unwrap();

    (StatusCode::OK, table_as_string).into_response()
}

pub async fn batches(State(state): State<ServerState>) -> Response {
    let batch_coll_dir = match BatchCollectionDir::try_from_dir(state.cfg.results_dir) {
        Ok(dir) => dir,
        Err(err) => {
            return (StatusCode::INTERNAL_SERVER_ERROR, Json(err.to_string())).into_response();
        }
    };

    let processed_batch_coll_dir =
        match PBatchCollectionDir::try_from_dir(state.cfg.processed_results_dir) {
            Ok(dir) => dir,
            Err(err) => {
                return (StatusCode::INTERNAL_SERVER_ERROR, Json(err.to_string())).into_response();
            }
        };

    let mut processed_summary_tables = HashMap::<String, Option<DataFrame>>::new();

    processed_batch_coll_dir
        .batch_dirs
        .iter()
        .for_each(|batch_dir| {
            let table = batch_dir.tables_dir.load_summary_total_table().ok();
            processed_summary_tables.insert(batch_dir.batch_name().into(), table);
        });

    let batch_info = batch_coll_dir.batch_dirs.iter().map(|batch_dir| {
        (
            batch_dir
                .path
                .file_stem()
                .unwrap()
                .to_str()
                .unwrap()
                .to_owned(),
            batch_dir.config_file.load_data(),
        )
    });

    let maybe_error: Vec<String> = batch_info
        .clone()
        .filter(|(_name, config_res)| config_res.is_err())
        .take(1)
        .map(|(_name, config_res)| config_res.unwrap_err().to_string())
        .collect();

    if !maybe_error.is_empty() {
        println!("Errors {:?}", maybe_error);
        return (
            StatusCode::INTERNAL_SERVER_ERROR,
            Json(maybe_error.first().unwrap().to_owned()),
        )
            .into_response();
    }

    let batch_info = batch_coll_dir
        .batch_dirs
        .iter()
        .map(|batchdir| {
            let batch_name = batchdir
                .path
                .file_stem()
                .unwrap()
                .to_str()
                .unwrap()
                .to_owned();

            let is_processed = processed_summary_tables.contains_key(&batch_name);
            let solved_count = if is_processed {
                let df = processed_summary_tables
                    .get(&batch_name)
                    .unwrap()
                    .as_ref()
                    .unwrap();
                let value = match df.column("bks_hit_total").unwrap().get(0).unwrap() {
                    AnyValue::Int64(value) => Some(value as usize),
                    AnyValue::Int32(value) => Some(value as usize),
                    _ => None,
                };
                value
            } else {
                None
            };

            BatchInfo {
                name: batch_name,
                config: batchdir.config_file.load_data().unwrap(),
                solved_count,
                is_processed: Some(is_processed),
            }
        })
        .collect();

    (StatusCode::OK, Json(BatchesResponse { batch_info })).into_response()
}
