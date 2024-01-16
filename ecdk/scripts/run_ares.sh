#!/usr/bin/bash

function print_help () {
  echo """
  Usage: $0 options

  Options:
    -h: print this help message and exit
    -i FILE/DIR [FILE/DIR ...]: input for jobscript; REMEBER TO QUOTE WHOLE STRING!
    -o DIR: output directory for the job script; THIS WILL BE PREPENDED WITH APPROPRIATE PREFIX
    -k: pass --test-only to sbatch call (dry run)
    -b BIN: path to jssp solver binary
    -t TIMESPEC: time spec string (sbatch)
    -m MEMSPEC: memspec (per cpu) (sbatch)
    -n SERIESCOUNT: series count
    -p NCORES: number of cores to run on (sbatch)
    -c CFGFILE: config file for solver (optional & experimental)
   """
}
# -s: prepend output directory with path to group storage; DO NOT US
# -S: prepend output directory with path to scratch storage

assert_binary_exists () {
  if ! command -v "$1" &> /dev/null
  then
    echo "Look like $1 binary is missing. Aborting"
    exit 1
  fi
}

ecdk_dir=${HOME}/master/master-monorepo/ecdk
ecrs_dir=${HOME}/master/master-monorepo/ecrs
solver_bin=${HOME}/master/master-monorepo/bin/solver
metadata_file=${HOME}/master/master-monorepo/ecdk/data/metadata/instance_metadata_v2.txt
plggroup="plgglscclass"
grant="plglscclass23-cpu"

input_files=""
output_dir=""
config_file=""
series_count=50
max_proc=36
dry_run=1
timespec="24:00:00"
memspec="512M"

scratch_storage_dir="${SCRATCH}"
group_storage_dir="${MY_GROUPS_STORAGE}"  # This envvar is defined on Ares in my .bashrc


# https://stackoverflow.com/questions/192249/how-do-i-parse-command-line-arguments-in-bash
OPTIND=1
opt_str="hi:o:t:p:m:n:b:c:k"

while getopts "${opt_str}" opt
do
  case "${opt}" in
    h)
      print_help
      exit 0
      ;;
    i)
      input_files="${OPTARG}"
      ;;
    o)
      output_dir="${OPTARG}"
      ;;
    p)
      max_proc="${OPTARG}"
      ;;
    k)
      dry_run=0
      ;;
    t)
      timespec="${OPTARG}"
      ;;
    m)
      memspec="${OPTARG}"
      ;;
    n)
      series_count="${OPTARG}"
      ;;
    b)
      solver_bin="${OPTARG}"
      ;;
    c)
      config_file="${OPTARG}"
      ;;
  esac
done

shift $((OPTIND-1))

${input_files:?"Input files must be set"}
${output_dir:?"Output directory must be set"}

if [[ ! -f $metadata_file ]]; then
  echo "$metadata_file does not exist"
  exit 1
fi

if [[ (! -z "${config_file}") && (! -f "${config_file}") ]]; then
  echo "$config_file does not exist"
  exit 1
fi

output_dir="${scratch_storage_dir}/${output_dir}"
echo "Output will be put in ${output_dir}"

cd ${ecdk_dir}

module purge
module load python/3.10.8-gcccore-12.2.0
pip install -r requirements.txt

#sbatch ./src/main.py run -i data/instances/ft_instances -m data/metadata/instance_metadata_v2.txt -o output -n 10 -p 10 ./bin/jssp
#sbatch ./src/main.py run -i data/instances/ft_instances data/instances/la_instances -m data/metadata/instance_metadata_v2.txt -o output-ft-la-multicore -n 50 -p 36 ../bin/jssp

sbatch_args=(
  "--account=$grant"
  "--nodes=1"
  "--ntasks=1"
  "--partition=plgrid"
  "--time=$timespec"
  "--cpus-per-task=$max_proc"
  "--mem-per-cpu=$memspec"
)

if [[ $dry_run -eq 0 ]]; then
  sbatch_args+=("--test-only")
fi

sbatch_args+=(
  "./src/main.py"
  "run"
  "-i" $input_files
  "-o" "$output_dir"
  "-m" "$metadata_file"
  "-n" "$series_count"
  "-p" "$max_proc"
)

if [[ ! -z "$config_file" ]]; then
  sbatch_args+=("--config-file" "$config_file")
fi

sbatch_args+=("$solver_bin")

echo "Args: ${sbatch_args[@]}"
sbatch "${sbatch_args[@]}"

# sbatch \
#   --account $grant \
#   --nodes=1 \
#   --ntasks=1 \
#   --partition=plgrid \
#   --time=${timespec} \
#   --cpus-per-task=$max_proc \
#   --mem-per-cpu=$memspec \
#   ./src/main.py run -i $input_files -o $output_dir -m $metadata_file -n $series_count -p $max_proc $solver_bin

