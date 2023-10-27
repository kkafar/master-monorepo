#!/usr/bin/bash

ecdk_dir=${HOME}/master/ecdk
ecrs_dir=${HOME}/master/ecrs

cd ${ecdk_dir}

module purge
module load python/3.10.8-gcccore-12.2.0
pip install -r requirements.txt

#sbatch ./src/main.py run -i data/instances/ft_instances -m data/metadata/instance_metadata_v2.txt -o output -n 10 -p 10 ./bin/jssp
sbatch ./src/main.py run -i data/instances/ft_instances data/instances/la_instances -m data/metadata/instance_metadata_v2.txt -o output-ft-la-multicore -n 50 -p 36 ../bin/jssp

