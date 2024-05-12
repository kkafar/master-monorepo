use std::path::PathBuf;

use ecrs::{
    ga::Metrics,
    prelude::population::{self, PopulationGenerator},
};
use itertools::Itertools;

use crate::{parse::JsspInstanceLoadingError, stats::IndividualTelemetry};

use super::{individual::JsspIndividual, Edge, EdgeKind, JsspInstance, Machine, Operation};

pub struct JsspPopProvider {
    instance: JsspInstance,
    // This is public for debugging purposes
    pub operations: Vec<Operation>,
}

impl JsspPopProvider {
    pub fn new(mut instance: JsspInstance) -> Self {
        // Finding dimension of the chromosome -- total number of operations (later multiplied)
        let dim: usize = instance.cfg.n_ops;
        let n_jobs = instance.cfg.n_jobs;

        // Prepare mock operations
        let mut zero_op = Operation::new(0, 0, 0, None, Vec::new());
        let sink_op = Operation::new(dim + 1, 0, 0, None, Vec::from_iter(0..=dim));

        // Since https://github.com/kkafar/master-monorepo/issues/223
        // operations in instance are numbered starting from 1. Thus I do not have now
        // to shift any ids. Just insert the source & sink operations with ids 0 & dim + 1
        // respective.
        instance.jobs.iter_mut().for_each(|job| {
            job.iter_mut().for_each(|op| {
                // We want the predecessors to be in asceding order. I rely on this behaviour in
                // the JSSP solver later on. Do not change it w/o modyfing the algorithm.
                op.preds.insert(0, 0);
                op.edges_out.push(Edge {
                    neigh_id: JsspInstance::job_succ_of_op(op.id, n_jobs, dim).unwrap_or(dim + 1),
                    kind: EdgeKind::JobSucc,
                })
            });
            // job.last_mut().unwrap().edges_out.last_mut().unwrap().neigh_id = dim + 1;
            zero_op.edges_out.push(Edge {
                neigh_id: job.first().unwrap().id,
                kind: EdgeKind::JobSucc,
            });
        });

        let operations = [zero_op]
            .into_iter()
            .chain(instance.jobs.clone().into_iter().flatten())
            .chain([sink_op])
            .collect_vec();

        assert_eq!(operations.len(), dim + 2);

        Self { instance, operations }
    }

    pub fn generate_with_metadata(&mut self, metrics: &Metrics, count: usize) -> Vec<JsspIndividual> {
        population::tools::PointGenerator::new()
            .generate_with_single_constraint(2 * (self.operations.len() - 2), count, 0.0..1.0)
            .into_iter()
            .map(|chromosome| {
                let mut indv = JsspIndividual::new(
                    chromosome,
                    self.operations.clone(),
                    Vec::from_iter((0..self.instance.cfg.n_machines).map(Machine::new)),
                    usize::MAX,
                );
                indv.telemetry = IndividualTelemetry::new(metrics.generation, 0);
                indv
            })
            .collect()
    }

    #[cfg(test)]
    pub fn instance(&self) -> &JsspInstance {
        &self.instance
    }
}

impl PopulationGenerator<JsspIndividual> for JsspPopProvider {
    fn generate(&mut self, count: usize) -> Vec<JsspIndividual> {
        population::tools::PointGenerator::new()
            .generate_with_single_constraint(2 * (self.operations.len() - 2), count, 0.0..1.0)
            .into_iter()
            .map(|chromosome| {
                JsspIndividual::new(
                    chromosome,
                    self.operations.clone(),
                    Vec::from_iter((0..self.instance.cfg.n_machines).map(Machine::new)),
                    usize::MAX,
                )
            })
            .collect()
    }
}

impl TryFrom<PathBuf> for JsspPopProvider {
    type Error = JsspInstanceLoadingError;

    fn try_from(file: PathBuf) -> Result<Self, Self::Error> {
        assert!(file.is_file(), "Received path does not point to a file!");
        let instance = JsspInstance::try_from(&file)?;
        Ok(JsspPopProvider::new(instance))
    }
}

#[cfg(test)]
mod tests {
    use std::{path::PathBuf, str::FromStr};

    use itertools::Itertools;

    use crate::problem::{EdgeKind, JsspInstance};

    use super::JsspPopProvider;

    // struct OpDef {
    //     id: usize,
    //     machine: usize,
    //     duration: usize,
    // }
    //
    // impl From<(usize, usize, usize)> for OpDef {
    //     fn from(value: (usize, usize, usize)) -> Self {
    //         Self {
    //             id: value.0,
    //             machine: value.1,
    //             duration: value.2,
    //         }
    //     }
    // }

    fn get_instance_mini() -> JsspInstance {
        let path = PathBuf::from_str("data/instances/mock_instances/test01.txt").unwrap();
        let instance_loading_result = JsspInstance::try_from(&path);
        assert!(instance_loading_result.is_ok());
        instance_loading_result.unwrap()
    }

    #[test]
    fn source_and_sink_are_on_proper_positions_mini() {
        let instance = get_instance_mini();
        let provider = JsspPopProvider::new(instance);

        let instance = provider.instance();

        let sink_id = instance.cfg.n_ops + 1;

        assert_eq!(provider.operations.first().unwrap().id, 0);
        assert_eq!(provider.operations.last().unwrap().id, sink_id);
    }

    #[test]
    fn source_and_sink_ops_are_added_properly_mini() {
        let instance = get_instance_mini();
        let provider = JsspPopProvider::new(instance);

        let instance = provider.instance();

        // We want to verify whether source & sink are present & edges are added properly.

        assert_eq!(provider.operations.len(), instance.cfg.n_ops + 2);

        let op_source = provider.operations.first().unwrap();

        // There should be edge to first operation of every job
        assert_eq!(op_source.edges_out.len(), instance.cfg.n_jobs);
        assert_eq!(
            op_source
                .edges_out
                .iter()
                .filter(|edge| edge.kind == EdgeKind::JobSucc)
                .count(),
            instance.cfg.n_jobs
        );

        let sink_id = instance.cfg.n_ops + 1;

        assert_eq!(provider.operations.first().unwrap().id, 0);
        assert_eq!(provider.operations.last().unwrap().id, sink_id);

        // We want to iterate through every job operations and assert that there are forward job
        // edges.
        instance.jobs.iter().for_each(|job| {
            job.iter().tuple_windows().for_each(|(op_a, op_b)| {
                assert_eq!(
                    op_a.edges_out
                        .iter()
                        .filter(|edge| edge.neigh_id == op_b.id && edge.kind == EdgeKind::JobSucc)
                        .count(),
                    1
                );
            });
            assert_eq!(job.last().unwrap().edges_out.iter().filter(|edge| edge.neigh_id == sink_id && edge.kind == EdgeKind::JobSucc).count(), 1);
        })
    }
}
