---
State for 17.10.2023
---

# Data

Data files are available on GDrive. Download & unpack it.

# How to use the solver

1. Clone ecrs repo & check-in

```
git clone https://github.com/ecrs-org/ecrs.git ecrs && cd ecrs
```

2. Compile the solver

```
cargo build --example jssp --release
```

3. Run it 

```
cargo run --example jssp --release -- --input-file <input_file> --output-dir <output_dir>
```

or run the binary directly:

```
target/release/examples/jssp --input-file <input_file> --output-dir <output_dir>
```

In case `output_dir` does not exist it will be created. 

4. For most up to date usage information run the solver with `--help` option.

```
cargo run --example jssp --release -- --help
```



## Copy-paste friendly section

```
git clone https://github.com/ecrs-org/ecrs.git ecrs && cd ecrs
cargo build --example jssp --release
target/release/examples/jssp --input-file <input_file> --output-dir <output_dir>
```

# How does the solver work (right now!)

## Individual representation

Atm individual is represented as follows:

```rust
/// Models single solution to the JSSP problem instance
#[derive(Debug, Clone)]
pub struct JsspIndividual {
    /// Encoding of the solution. This can be decoded to the proper solution
    pub chromosome: Vec<f64>,
    /// Clone of all operations from the problem instance
    pub operations: Vec<Operation>,
    /// Clone of all machines from the problem instance
    pub machines: Vec<Machine>,
    /// If computed - fitness value of this solution. Check `is_fitness_valid`
    /// property to determine whether this value is up to date
    /// This is not an Option for some practical reasons
    /// TODO: But this should be an Option or some enum with additional information
    pub fitness: usize,
    /// If `true` the `fitness` field holds the value for the current `chromosome`
    /// and does need to be recomputed. This must be kept in sync!
    pub is_fitness_valid: bool,
    /// TODO: Determine what I've used it for
    is_dirty: bool,
}
```

### Chromosome

The length of the chromosome is `2 * n_operations` (same as in our base paper).

### Operation

Operation is currently defined as follows:

```rust
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
    /// this op is executed on. The value of this field is modified as the algorithm runs
    edges_out: Vec<Edge>,
    /// Operation id of direct machine predecessor of this op. This might be `None` in following scenarios:
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
```

### Machine

Machine is currently represented as follows:

```rust
/// Models the machine -- when it is occupied
#[derive(Debug, Clone)]
#[allow(dead_code)]
pub struct Machine {
    /// Unique id of the machine
    id: usize,
    /// Remaining machine capacity. If a range is added -> this means that the machine is occupied in that range
    rmc: Vec<Range<usize>>,
    pub last_scheduled_op: Option<usize>,
}
```

## The algorithm

1. Generate population
3. Loop for given number of iterations (`n_generations`):
    
    1. Evaluate population
    2. Run selection operator
    3. Run crossover operator
    4. Run mutation operator
    5. Evaluate children if needed
    6. Run replacement operator

### Population generator

* The population is sampled (points from the R^n space) from uniform U(0, 1) distribution.
* The population size is equal to `2 * n_operations` (following the paper here)

### Population evalutaion

In general:

1. Decode the solution from numeric chromosome
2. Earlier step creates schedule (precedence relation between the jobs and assignment to machines).
Such schedule can be interpreted as a graph.
We find the longest path in this graph -- this is our makespan.
We then try to improve the makespan by determining critical blocks & swapping "edge operations". If there is no improvement 
we restore original solution.
A ciritcal block is roughly a set of adjacent operations executed on the same machine that lies on critical path.
(For more rigorous definition I delegate you to the paper or we can discuss it as it is blurry).


### Selection operator

Standard `Rank` selection is being used right now:

Individuals are selected by randomly (uniform distribution) choosing pairs of individuals - better
rated individual from selected pair goes to mating pool. In case of equal fitness - only one goes to mating pool.

**Note**: The same individual *can* be selected multiple times.

### Crossover operator

Customized, implemented as defined in the paper (I need to verify it, whether I've not omitted somthing).
The general idea is:

* 2 parents as input, 2 children as output
* Iterate over zipped parent's chromosomes: with the probability of 0.6 current allele of first parent goes
to first child, current allele of second parent goes to the second child. With probability of 0.4 we do it crosswise. 

Note: Possible twist: select with probability 0.6 the allele from better parent?

### Mutation operator

Identity. I mention it here because it is used in code, as ECRS requries it. 

### Replacement operator

`elite_rate == 0.1` 
`sample_rate == 0.2`

1. The population is sorted (please note here that parent-children index-based relation is destroyed after this operator)
2. The `elite_rate * pop_size` individuals are put to the front of the population vector
3. The last (in sorted array - the worst )`sample_rate * pop_size` individuals are replaced by random sample
4. The rest of the population (not the elite, and not the newly generated ones) is replaced by children from the crossover

### Stop condition

The solver stops after 400 iterations (generations +- 1)

Currently in the code the second stop conditiond is defined: max run duration: 30 secs. This is mostly for debugging
puroposes & speeding up testing. Can be removed by commenting out single line in solvers `main` function.

