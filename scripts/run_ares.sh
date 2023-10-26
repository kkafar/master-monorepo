#!/usr/bin/bash

ecdk_dir=${HOME}/master/ecdk
ecrs_dir=${HOME}/master/ecrs

cd ${ecdk_dir}

sbatch ./src/main.py run -i data/instances/ft_instances -m data/metadata/instance_metadata_v2.txt -o output -n 10 -p 10 ../ecrs/target/release/examples/jssp

