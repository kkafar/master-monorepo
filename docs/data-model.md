# Input file outline

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

# Solution file outline



# CSV output files outline

CSV OUTLINE:

```csv
event_name,additional_information,...

newbest,<generation>,<total_duration>,<fitness>
diversity,<generation>,<total_duration>,<population_size>,<diversity>
bestingen,<generation>,<total_duration>,<fitness>
popgentime,<time>
iterinfo,<generation>,<eval_time>,<sel_time>,<cross_time>,<mut_time>,<repl_time>,<iter_time>
```
