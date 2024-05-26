# Nomenclature

## Basic terms

Few basic terms that do have use cases across the codebase:

* experiment - given experiment instance, that has well-defined number of jobs, machines, operations and relations between them,
* experiment id - string describing particular experiment, e.g. `ft06`, `la40`,
* experiment series / series - as given experiment can be run multiple times to take averages of statistics, each such run is called a series,
* experiment family - the most straightforward definition would be that experiments with common id prefixes belong to the same experiment family, e.g. `ft`, `la`,
* experiment batch - set of experiments.

## Resulting code terms

* `ExperimentBatch` is a set of `Experiments`.
* Single `Experiment` consists from a number of `Series`. 
* All `Series` that given `Experiment` consists of are run for single test case.
* Single `Series` is a single solver run and its outputs.


