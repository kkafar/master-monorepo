# Input file outline

## Standard specification

First line of each file:

```
n_jobs n_machines
```

Each of `n_jobs` following lines describes single job (in order from 1 to `n_jobs`).
Each job description is of format:

```
op_1_machine_id op_1_duration op_2_machine_id op_2_duration ...
```

Number of operations per single job is not specified and must
be determined dynamically.

Note 1: *Quick inspection of current data files indicates that each job
consists of the same number of operations*

Note 2: *Even if it changes it is always possible to add padding (jobs with duration 0
and assigned to any machine)*

**Note 3**: *Machines are numbered from 0 upwards!*

**Note 4**: *The order of operation execution (precedence) is such, that for any given operation 
op_i all operations op_k (k < i && op_k in the same job as op_i) must be completed)*


## Taillard specification

On the first line there are two numbers. 
The first is the number of jobs and the second number of machines.

```
n_jobs n_machines
```

Following there are two matrices. First with a line for each job containing
processing time for each operation. Second with the order of visiting machines.

*Note 1*: *The numbering of machines starts at 1*


# Solution

Solutions are available in various formats:

## Operation order & hash value

1. For a given solution sort operations by their respective finish times.

For operations with equal end times any operation with no duration is always after all operations with a duration.
If tie still appears, operation with lower machine index comes first.

2. Convert sorted array of operations to a string of ids separated by '_', e.g.: "2_3_1_4".
3. Calculate MD5 hash for such string <-- this is the result.

## All solutions in a single file

All best solutions for a given instance are inside this file.
The file consists of a single line per solutions.
On every line the operations are numbered according to the operation order described above.

## Solution order file

Each line specifies the order of the jobs for a given machine.

## Solution start file

The solution start file gives a matrix with row per job and a column per machine. The values are start times of the operations.

If `M[1][0] == 10` ==> Job 2 starts on machine 0 (1) at time 10.

# Metadata file

Provider:
`https://github.com/thomasWeise/jsspInstancesAndResults#3-provided-data`

CSV with following schema:

```csv
inst.id,inst.ref,inst.jobs,inst.machines,inst.opt.bound.lower,inst.opt.bound.lower.ref,inst.bks,inst.bks.ref,inst.bks.time,inst.bks.time.ref
```

where:

* `id` (`inst.id`) - the unique identifier of the instance
* `ref` (`inst.ref`) - reference to the publication (this is available via repo)
* `jobs` (`inst.jobs`) - the number of jobs in the instance
* `machines` (`inst.machines`) - the number of machines in the instance
* `lb` (`inst.opt.bound.lower`) - the lower bound for the makespan of any solution for the instance
* `lb ref` (`inst.opt.bound.lower.ref`) - the reference to the earliest publication that mentioned this lower bound (available via repo)
* `bks` (`inst.bks`) - the makespan of the best-known solution
* `bks ref` (`inst.bks.ref`) - ...
* `bks time` (`inst.bks.time`) - ignore
* `bks time ref` (`inst.bks.time.ref`) - ignore

# CSV output files outline

Solver logs additional run metadata in following format:

CSV OUTLINE:

```csv
event_name,additional_information,...

newbest,<generation>,<total_duration>,<fitness>
diversity,<generation>,<total_duration>,<population_size>,<diversity>
bestingen,<generation>,<total_duration>,<fitness>
popgentime,<time>
iterinfo,<generation>,<eval_time>,<sel_time>,<cross_time>,<mut_time>,<repl_time>,<iter_time>
```

# Reference

Data & formats are taken from [the website](http://jobshop.jjvh.nl/): http://jobshop.jjvh.nl/
