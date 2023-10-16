# Goals

Main goal of this software is to provide tools for running jssp solver & analyze solver's output

# Functionalities

## User stories

### Python app

1. [ ] I want to run & configure solver
2. [x] I want to specify input files and directories with input files via cli
3. [x] I want to specify metada file path via cli
4. [ ] I want to specify run-config file with JSON run configuration via cli
5. [ ] I want the program to plot various graphs:
    1. [ ] Graph 1
6. [x] I want to run many solver instances in parallel
7. [ ] I want to run solver only, skipping data analysis
8. [ ] I want to run analysis only, skipping solver run
9. [ ] I want to specify input data for all kind of runs
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


