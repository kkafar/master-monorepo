#!/usr/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --partition=plgrid
#SBATCH --time=00:20:00
#SBATCH --account=plglscclass23-cpu

ecdk_dir=${HOME}/master/master-monorepo/ecdk
ecrs_dir=${HOME}/master/master-monorepo/ecrs

# $1: module name
function load_module_if_needed() {
  module_name=$1
  if [[ $(module is-loaded ${module_name}) -ne 0 ]]; then
    module add ${module_name}
  fi
}

cd ${ecdk_dir}

load_module_if_needed python/3.10.8-gcccore-12.2.0-bare
pip install -r requirements.txt
