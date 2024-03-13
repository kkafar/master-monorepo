# Goals

Main goal of this software is to provide tools for running jssp solver & analyze solver's output

# Functionalities

## User stories

### Python app

1. [x] I want to run & configure solver
2. [x] I want to specify input files and directories with input files via cli
3. [x] I want to specify metada file path via cli
4. [x] I want to specify run-config file with JSON run configuration via cli
5. [x] I want the program to plot various graphs:
6. [x] I want to run many solver instances in parallel
7. [x] I want to run solver only, skipping data analysis
8. [x] I want to run analysis only, skipping solver run
9. [x] I want to specify input data for all kind of runs
10. [x] I want to specify output directory for the data
11. [x] Each run of the program, if any data is produced,
        should put all produced data inside timestamped directory
12. [x] Each experiment result should be put inside dedicated directory
13. [x] Each series of given experiment should have its dedicated directory


### Solver

1. [x] Solver should produce separate file for each event type
2. [x] Solver should put all produced files into indicated directory
3. [x] Solver output files should be named as specified in `Solver naming patterns` section
4. [x] Solver should take two parameters:
    1. [x] `--input-file` - Path to file with problem instance specification
    2. [x] `--output-dir` - Path to the directory (may not exist, if it is the case: create it) where output files should be put


## Solver output structure

Please note that the solver takes only two parameters (see [Solver section](#Solver)) and most of these requirements should be implemented
by the python scripts.

1. [x] For each event there should be separate file produced named with respect to pattern: `event_<event_name>.csv`
2. [x] There should be additional JSON file produced with following keys:
    1. [x] `solution_string` - solution string constructed as described in [data model docs](./data-model.md)
    2. [x] `hash` - MD5 hash of the `solution_string`
    3. [x] `fitness` - fitness of the best individual
    4. [x] `generation_count` - number of computed generations
    5. [x] `total_time` - duration in ms of the solver run
    6. [x] `chromosome` - chromosome of the individual
    In case no solution was found, these fields should be nulls (but the entries should exist).
    The file should be named `run_metadata.json`.
3. [ ] Most parameters of the evolution process should be possible to specifiy via the cli


# Architecture refactor

## Run command

### Goal

The goal of the command is not only to run the solver, but to run it with given strategy and environment.
On local, developement environment, I want to be able to run given count of solver instances in paralell and collect
the outputs in a structurized way, so that the post processing is easier, and unified between outputs from different environment.

The second, more important environment is Ares, as that's the main platform for conducing computation.
In this case, I want to be able to run either the local runner on single node with given number of cpus (single solver 
process per CPU) or (higher priority) utilize `HyperQueue` software (as it is already done), so that I can better utilize 
Ares resources.

So, to put it in more specific terms, I want to provide a list of input files / directories with input files,
and get single output directory with all result data. Preferably, zipped & ready for further processing steps.
The computation steps should be abstracted away and envrionment / parameter dependent (local / Ares).

The CLI should make it possible to pass parameters to solver binary either through config file (which is parsed by the solver,
so the only responsibility of the program is to pass the path through) or providing (suggestion) some namespaced parameters,
e.g. `--solver-xxx` or `--sv-xxx`.


### Architecture discussion

#### What do the program needs to do?

1. Take file list of instance specs & other parameter,
2. convert input into set of tasks, that will be then passed alongisde other paramethers to appropriate runtime,
3. the runtime is responsible for: 
    1. scheduling the tasks in appropriate way; in case of `local` runtime 

#### What specs do I need?

#### What utilities do I need?

#### How should I organize that?

What do I need?

1. [ ] Input specification
2. [ ] Runtime abstraction
3. [ ] Runtime specific task abstraction (if necessary)
4. [ ] Way to convert input to set of tasks to compute


