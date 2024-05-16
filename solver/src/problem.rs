use std::ops::Range;

use itertools::Itertools;

pub mod crossover;
pub mod fitness;
pub mod individual;
pub mod population;
pub mod probe;
pub mod replacement;
pub mod selection;

/// Describes relation between two operations
#[derive(Debug, Clone, PartialEq, Eq, Copy)]
pub enum EdgeKind {
    /// Operation that the edge points to is from the same job (ops are on different machines)
    JobSucc,
    /// Operation that the edge points to is on the same machine (ops are from different jobs)
    MachineSucc,
}

/// Models the edge in neighbourhood graph where operations are nodes
#[derive(Debug, Clone, Copy)]
pub struct Edge {
    /// Unique id of the neighbour operation
    pub neigh_id: usize,
    /// Describes the relation between the operations
    pub kind: EdgeKind,
}

impl Edge {
    pub fn new(neigh_id: usize, kind: EdgeKind) -> Self {
        Self { neigh_id, kind }
    }
}

/// Models Operation that is a part of some job
///
/// TODO: Cleanup this struct.
/// 1. Move all data non-intrinsic to the Operation model to separate structs
/// 2. `critical_distance` should be an Option
#[derive(Debug, Clone)]
pub struct Operation {
    /// Unique id of this operation
    id: usize,
    /// Duration of the operation
    duration: usize,
    /// Machine this operation is assigned to
    machine: usize,
    /// Finish time tick of this operation as determined by the solver. The value of this field
    /// is modified during the algorithm run
    finish_time: Option<usize>,
    /// Ids of all ops that this op depends on. TODO: Was the order guaranteed?
    preds: Vec<usize>,
    /// Edges describing relations to other ops in neighbourhood graph. It contains *at most* two elements
    /// as each op might have at most two successors: next operation in the job or next operation on the same machine
    /// this op is executed on. The value of this field is modified as the algorithm runs.
    /// NOTE: In current implementation is contains either one or two elements. The first one is
    /// always present and is a JobSuccsor. The second one is optional and is a MachineSuccesor,
    /// which is filled during individual evaluation. There is one expception: dummy sink
    /// operation, which won't have any Edge in this vector.
    edges_out: Vec<Edge>,
    /// Operation id of direct machine predecessor of this op. This might be `None` in following scenarios:
    ///
    /// 1. Op is the first op on particular machine TODO: I'm not sure now, whether I set op no. 0 as machine predecessor
    /// of every first op on given machine or not, so please verify it before using this fact.
    /// 2. This is op with id 0
    ///
    /// The value of this field is modified as the algorithm runs.
    machine_pred: Option<usize>,
    /// If this operation lies on critical path in neighbourhood graph (as defined in paper by Nowicki & Smutnicki)
    /// this is the edge pointing to next op on critical path, if there is one - this might be the last operation
    /// or simply not on the path. The value of this field is modified as the algorithm runs.
    critical_path_edge: Option<Edge>,
    /// If this operation lies on critical path this field is used by the local search algorithm to store
    /// distance from this op to the sink node. The value of this field is modified as the algorithm runs.
    critical_distance: usize,
}

impl Operation {
    pub fn new(
        id: usize,
        duration: usize,
        machine: usize,
        finish_time: Option<usize>,
        preds: Vec<usize>,
    ) -> Self {
        Self {
            id,
            duration,
            machine,
            finish_time,
            preds,
            edges_out: Vec::new(),
            machine_pred: None,
            critical_path_edge: None,
            critical_distance: usize::MIN, // TODO: Should MIN be used here?
        }
    }

    /// Resets the state of the operation so that this object can be reused to find new solution
    pub fn reset(&mut self) {
        self.finish_time = None;
        self.machine_pred = None;
        // Job edges are determined by the problem instance we consider, while machine edges
        // are determined by the scheduling process
        if let Some(edge_to_rm) = self
            .edges_out
            .iter()
            .find_position(|edge| edge.kind == EdgeKind::MachineSucc)
        {
            self.edges_out.swap_remove(edge_to_rm.0);
        }
        debug_assert_eq!(
            self.edges_out
                .iter()
                .filter(|e| e.kind == EdgeKind::MachineSucc)
                .count(),
            0
        );

        self.critical_path_edge = None;

        // TODO: Should we zero `critical_path_edge` and `critical_distance` here?
        // Why is it not done?
    }

    #[cfg(test)]
    pub fn id(&self) -> usize {
        self.id
    }

    #[cfg(test)]
    pub fn duration(&self) -> usize {
        self.duration
    }

    #[cfg(test)]
    pub fn machine_id(&self) -> usize {
        self.machine
    }

    #[cfg(test)]
    pub fn preds(&self) -> &Vec<usize> {
        &self.preds
    }
}

#[derive(Debug, Clone)]
pub struct MachineAllocation {
    /// Id of the operation
    op_id: usize,

    /// Period of allocation
    range: Range<usize>,
}

impl MachineAllocation {
    pub fn new(op_id: usize, range: Range<usize>) -> Self {
        Self { op_id, range }
    }
}

#[derive(Debug, Clone, Copy)]
pub struct MachineNeighs {
    pred: Option<usize>,
    succ: Option<usize>,
}

impl MachineNeighs {
    pub fn new(pred: Option<usize>, succ: Option<usize>) -> Self {
        Self { pred, succ }
    }
}

/// Models the machine -- when it is occupied
#[derive(Debug, Clone)]
#[allow(dead_code)]
pub struct Machine {
    /// Unique id of the machine
    id: usize,

    // For naive implementation
    // rmc: Vec<usize>,
    /// Remaining machine capacity. If a range is added -> this means that the machine is occupied in that range
    // For "possibly better implementation"
    rmc: Vec<MachineAllocation>,
    // pub last_scheduled_op: Option<usize>,
    // pub last_scheduled_range: Option<Range<usize>>,
}

impl Machine {
    pub fn new(id: usize) -> Self {
        Self {
            id,
            // rmc: vec![1; rmc_capacity],
            rmc: Vec::new(),
            // last_scheduled_op: None,
            // last_scheduled_range: None,
        }
    }
}

// Possibly better implementation
// Best one should be balanced interval BST (e.g. BTreeMap) with simple interval intersection
// finding algorithm.
// Unfortunately the API that would allow implementation of such algorithm is not stabilized yet:
// https://github.com/rust-lang/libs-team/issues/141
// Example implementation: https://github.com/Amanieu/rangetree
//
// Here we use just a vector of intervals. This is most likely slower that naive solution, but it
// does not require so much memory.
impl Machine {
    pub fn is_idle(&self, query: Range<usize>) -> bool {
        !self
            .rmc
            .iter()
            .any(|alloc| alloc.range.start < query.end && alloc.range.end > query.start)
    }

    /// Allocates given range on the machine, marking it as occupied in range
    /// [range.start, range.end).
    ///
    /// DOES NOT PERFORM VALIDATION!
    /// Make sure via `is_idle` method that the machine is not occupied in the span
    /// you want to reserve.
    ///
    pub fn reserve(&mut self, range: Range<usize>, op: usize) -> MachineNeighs {
        // if let Some(ref last_scheduled_range) = self.last_scheduled_range {
        //     if range.end <= last_scheduled_range.start {
        //         warn!("Scheduling operation {} on machine {} at {:?} BEFORE already scheduled operation {} at {:?}", op, self.id, &range, self.last_scheduled_op.unwrap(), last_scheduled_range);
        //     }
        // }

        self.rmc.push(MachineAllocation::new(op, range.clone()));

        // We look for successor & predecessor naively. TODO: Use a better data structure here...
        let lower_bound = self
            .rmc
            .iter()
            .filter(|alloc| alloc.range.end <= range.start)
            .max_by_key(|alloc| alloc.range.end);
        let upper_bound = self
            .rmc
            .iter()
            .filter(|alloc| alloc.range.start >= range.end)
            .min_by_key(|alloc| alloc.range.start);

        // self.last_scheduled_op = Some(op);
        // self.last_scheduled_range = Some(range);

        MachineNeighs::new(
            lower_bound.map(|alloc| alloc.op_id),
            upper_bound.map(|alloc| alloc.op_id),
        )
    }

    /// Removes all ranges from the machine state allowing instance of this type to be reused
    pub fn reset(&mut self) {
        self.rmc.clear();
        // self.last_scheduled_op = None;
        // self.last_scheduled_range = None;
    }
}

/// Basic information (metadata) about the jssp instance.
#[derive(Debug, Clone)]
pub struct JsspConfig {
    /// Total number of jobs. Note that the job/operation naming/meaning is not consistent.
    /// TODO: Unify this so that job is a ordered set of operations.
    pub n_jobs: usize,
    /// Total number of machines in this problem instance
    pub n_machines: usize,
    /// Total number of operations. Note that the job/operation naming/meaning is not consistent across
    /// the codebase (but also in article...)
    pub n_ops: usize,
}

#[derive(Debug, Clone)]
pub struct JsspInstanceMetadata {
    /// Name of the instance. In case the instance was loaded from the disk,
    /// the `name` should be related to the data file name.
    pub name: String,
}

/// Describes single JSSP problem instance.
/// Instance is modeled as a set of jobs.
/// Each job is modeled as a set of operations.
/// Operations have precedency relation estabilished
/// and each operation is assigned to a particular machine.
#[derive(Debug, Clone)]
pub struct JsspInstance {
    /// Jobs are numerated with ids from 0 upwards.
    /// Operations are assigned ids from 0 upwards, in order.
    pub jobs: Vec<Vec<Operation>>,
    pub cfg: JsspConfig,
    // TODO: I should merge Instance metadata with config
    pub metadata: JsspInstanceMetadata,
}

impl JsspInstance {
    //! These methods are implemented according to decisions undertaken
    //! in https://github.com/kkafar/master-monorepo/discussions/277

    /// Returns "global" id of k'th operation of job j.
    /// Note that it is assumed that k >= 1.
    /// This method panics when k < 1.
    /// It **might** return invalid result for invalid input, e.g.
    /// when job j does not have kth operation.
    ///
    /// IMPORTANT:
    /// Complying to https://github.com/kkafar/master-monorepo/discussions/277,
    /// JOBS use 0-based numbering,
    /// OPERATIONS use 1-based numbering,
    /// MACHINES use 0-based numbering.
    /// Moreover, since https://github.com/kkafar/master-monorepo/issues/223
    /// operations are numbered in specific way. See the issue for details.
    #[inline]
    pub fn id_of_kth_op_of_job_j(k: usize, j: usize, n_jobs: usize) -> usize {
        assert!(k >= 1);
        (k - 1) * n_jobs + j + 1
    }

    /// Returns 0-based job id for operation with given id.
    /// This method assumes that input is valid.
    /// Expect garbage output for garbage input.
    ///
    /// IMPORTANT:
    /// Complying to https://github.com/kkafar/master-monorepo/discussions/277,
    /// JOBS use 0-based numbering,
    /// OPERATIONS use 1-based numbering,
    /// MACHINES use 0-based numbering.
    /// Moreover, since https://github.com/kkafar/master-monorepo/issues/223
    /// operations are numbered in specific way. See the issue for details.
    #[inline]
    pub fn job_id_of_op(op_id: usize, n_jobs: usize) -> usize {
        // We subtract 1 as operations are numbered from 1, and jobs are numbered from 0.
        (op_id - 1) % n_jobs
    }

    /// Returns which operation in turn of its job this operation is.
    /// Correct result should be >= 1.
    /// Expect garbage output for garbage input.
    ///
    /// IMPORTANT:
    /// Complying to https://github.com/kkafar/master-monorepo/discussions/277,
    /// JOBS use 0-based numbering,
    /// OPERATIONS use 1-based numbering,
    /// MACHINES use 0-based numbering.
    /// Moreover, since https://github.com/kkafar/master-monorepo/issues/223
    /// operations are numbered in specific way. See the issue for details.
    #[inline]
    pub fn op_offset_in_job(op_id: usize, n_jobs: usize) -> usize {
        op_id.div_ceil(n_jobs)
    }

    /// Returns **newly allocated** vector of operations ids, that are job predecessors
    /// of operation with given id. Note that this computation is not cached! Each call
    /// to this method repeats the computation.
    ///
    /// Note also that this method does not include source (0) / sink (nm + 1) operations since these
    /// are solver specific - not all approaches utilise this.
    ///
    /// This method **does** guarantee that the predecessors are in order, i.e.
    /// for any given indice `i` of output array `result`, for any `0 <= j < i`, operation with id
    /// `result[j]` a  job predecessor of op with id `result[i]`.
    ///
    /// IMPORTANT:
    /// Complying to https://github.com/kkafar/master-monorepo/discussions/277,
    /// JOBS use 0-based numbering,
    /// OPERATIONS use 1-based numbering,
    /// MACHINES use 0-based numbering.
    /// Moreover, since https://github.com/kkafar/master-monorepo/issues/223
    /// operations are numbered in specific way. See the issue for details.
    pub fn generate_predecessors_of_op_with_id(op_id: usize, n_jobs: usize) -> Vec<usize> {
        // op_id is kth operation of its job, thus there will be (k - 1) elemnts in result vector.
        let k = JsspInstance::op_offset_in_job(op_id, n_jobs);
        let j = JsspInstance::job_id_of_op(op_id, n_jobs);

        // TODO(perf): possible optimisation here, we do not need to compute each id individually,
        // p + 1 can be derived from pth id by adding n_jobs.
        Vec::from_iter((1..k).map(|pred_k| JsspInstance::id_of_kth_op_of_job_j(pred_k, j, n_jobs)))
    }

    /// Returns job successor of given operation, or None if there isn't one.
    ///
    /// Note that this method does not take into account any source / sink operations,
    /// as these are solver / implementation dependent.
    ///
    /// IMPORTANT:
    /// Complying to https://github.com/kkafar/master-monorepo/discussions/277,
    /// JOBS use 0-based numbering,
    /// OPERATIONS use 1-based numbering,
    /// MACHINES use 0-based numbering.
    /// Moreover, since https://github.com/kkafar/master-monorepo/issues/223
    /// operations are numbered in specific way. See the issue for details.
    pub fn job_succ_of_op(op_id: usize, n_jobs: usize, n_ops: usize) -> Option<usize> {
        if op_id + n_jobs <= n_ops {
            Some(op_id + n_jobs)
        } else {
            None
        }
    }

    /// Returns job predecessor of given operation, or None if there isn't one.
    ///
    /// Note that this method does not take into account any source / sink operations,
    /// as these are solver / implementation dependent.
    ///
    /// IMPORTANT:
    /// Complying to https://github.com/kkafar/master-monorepo/discussions/277,
    /// JOBS use 0-based numbering,
    /// OPERATIONS use 1-based numbering,
    /// MACHINES use 0-based numbering.
    /// Moreover, since https://github.com/kkafar/master-monorepo/issues/223
    /// operations are numbered in specific way. See the issue for details.
    #[allow(dead_code)]
    pub fn job_pred_of_op(op_id: usize, n_jobs: usize) -> Option<usize> {
        if let Some(sub) = op_id.checked_sub(n_jobs) {
            if sub >= 1 {
                Some(sub)
            } else {
                None
            }
        } else {
            None
        }
    }
}

#[cfg(test)]
mod tests {
    use super::JsspInstance;

    #[test]
    fn id_of_kth_op_of_job_j_computed_correctly_test03() {
        let n_jobs = 3;
        let _n_machines = 4;

        // According to the used problem modeling each job should have 4 operations (n_machines)
        // and each machine should be assigned 3 operations (n_jobs).

        let job_0_expected_ids = [1, 4, 7, 10];
        let job_1_expected_ids = [2, 5, 8, 11];
        let job_2_expected_ids = [3, 6, 9, 12];

        let job_expected_ids = [job_0_expected_ids, job_1_expected_ids, job_2_expected_ids];

        for (job_id, expected_ids) in job_expected_ids.iter().enumerate() {
            expected_ids
                .iter()
                .enumerate()
                .map(|(index, id)| (index + 1, id))
                .for_each(|(op_number, &expected_id)| {
                    assert_eq!(JsspInstance::id_of_kth_op_of_job_j(op_number, job_id, n_jobs), expected_id);
                })
        }
    }

    #[test]
    fn job_id_of_op_computed_correctly_test03() {
        let n_jobs = 3;
        let _n_machines = 4;

        // According to the used problem modeling each job should have 4 operations (n_machines)
        // and each machine should be assigned 3 operations (n_jobs).

        let job_0_ids = [1, 4, 7, 10];
        let job_1_ids = [2, 5, 8, 11];
        let job_2_ids = [3, 6, 9, 12];

        let job_ops_ids = [job_0_ids, job_1_ids, job_2_ids];

        for (job_id, job_operation_ids) in job_ops_ids.iter().enumerate() {
            for &op_id in job_operation_ids {
                assert_eq!(JsspInstance::job_id_of_op(op_id, n_jobs), job_id);
            }
        }
    }

    #[test]
    fn op_offset_in_job_test03() {
        let n_jobs = 3;
        let _n_machines = 4;

        // According to the used problem modeling each job should have 4 operations (n_machines)
        // and each machine should be assigned 3 operations (n_jobs).

        let job_0_ids = [1, 4, 7, 10];
        let job_1_ids = [2, 5, 8, 11];
        let job_2_ids = [3, 6, 9, 12];

        let job_ops_ids = [job_0_ids, job_1_ids, job_2_ids];

        for (_job_id, job_operation_ids) in job_ops_ids.iter().enumerate() {
            for (expected_op_offset, &op_id) in job_operation_ids.iter().enumerate().map(|(index, op_id)| (index + 1, op_id)) {
                assert_eq!(JsspInstance::op_offset_in_job(op_id, n_jobs), expected_op_offset);
            }
        }
    }

    #[test]
    fn job_succ_of_op_computed_correctly_test03() {
        let n_jobs = 3;
        let n_machines = 4;
        let n_ops = n_jobs * n_machines;

        // According to the used problem modeling each job should have 4 operations (n_machines)
        // and each machine should be assigned 3 operations (n_jobs).

        let job_0_ids = [1, 4, 7, 10];
        let job_1_ids = [2, 5, 8, 11];
        let job_2_ids = [3, 6, 9, 12];

        let job_ops_ids = [job_0_ids, job_1_ids, job_2_ids];

        for (_job_id, job_operation_ids) in job_ops_ids.iter().enumerate() {
            for (index, &op_id) in job_operation_ids.iter().enumerate() {
                if index < job_operation_ids.len() - 1 {
                    assert_eq!(JsspInstance::job_succ_of_op(op_id, n_jobs, n_ops), Some(job_operation_ids[index + 1]));
                } else {
                    assert_eq!(JsspInstance::job_succ_of_op(op_id, n_jobs, n_ops), None);
                }
            }
        }
    }

    #[test]
    fn job_pred_of_op_computed_correctly_test03() {
        let n_jobs = 3;
        let _n_machines = 4;

        // According to the used problem modeling each job should have 4 operations (n_machines)
        // and each machine should be assigned 3 operations (n_jobs).

        let job_0_ids = [1, 4, 7, 10];
        let job_1_ids = [2, 5, 8, 11];
        let job_2_ids = [3, 6, 9, 12];

        let job_ops_ids = [job_0_ids, job_1_ids, job_2_ids];

        for (_job_id, job_operation_ids) in job_ops_ids.iter().enumerate() {
            for (index, &op_id) in job_operation_ids.iter().enumerate() {
                if index > 0 {
                    assert_eq!(JsspInstance::job_pred_of_op(op_id, n_jobs), Some(job_operation_ids[index - 1]));
                } else {
                    assert_eq!(JsspInstance::job_pred_of_op(op_id, n_jobs), None);
                }
            }
        }
    }

    #[test]
    fn generate_predecessors_of_op_with_id_computed_correctly_test03() {
        let n_jobs = 3;
        let _n_machines = 4;

        // According to the used problem modeling each job should have 4 operations (n_machines)
        // and each machine should be assigned 3 operations (n_jobs).

        let job_0_ids = [1, 4, 7, 10];
        let job_1_ids = [2, 5, 8, 11];
        let job_2_ids = [3, 6, 9, 12];

        let job_ops_ids = [job_0_ids, job_1_ids, job_2_ids];

        for (job_id, job_operation_ids) in job_ops_ids.iter().enumerate() {
            for (index, &op_id) in job_operation_ids.iter().enumerate() {
                let preds = JsspInstance::generate_predecessors_of_op_with_id(op_id, n_jobs);

                if index == 0 {
                    assert!(preds.is_empty());
                } else {
                    assert_eq!(preds.len(), index);
                    job_operation_ids.iter().take(index).zip(preds).for_each(|(&expected_id, generated_id)| {
                        assert_eq!(expected_id, generated_id);
                    })
                }
            }
        }


    }
}
