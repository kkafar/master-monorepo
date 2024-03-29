# !/bin/bash
#!/usr/bin/bash

function assert_envvar_set() {
  local cmdname=$1
  if [ -z "${!cmdname}" ]; then
      echo "$cmdname is unset or set to the empty string"
      exit 1
  fi
}

function load_module_if_needed() {
  local module_name=$1
  module is-loaded ${module_name}
  local retval=$(echo $?)
  if [[ ${retval} -ne 0 ]]; then
    module add ${module_name}
  fi
}

function start_hq_server_if_needed() {
  hq server info 2> /dev/null
  local retval=$(echo $?)
  if [[ ${retval} -ne 0 ]]; then
    echo "Seems that HyperQueue server is not running, starting one..."
    nohup hq server start &
    echo "Sleeping for 5s to let server start in background..."
    sleep 5
  else
    echo "Seems that HyperQueue server is already running"
  fi
}

function create_auto_alloc_queue_if_needed() {
  local line_count=$(hq alloc list | wc -l)
  # Relying on structure of command output here
  if [[ ${line_count} -eq 3 ]]; then
    echo "Seems that there are no auto allocation queues present, attempting to create one..."
    # hq alloc add slurm \
    #   --workers-per-alloc 1 \
    #   --max-worker-count 48 \
    #   --backlog 36 \
    #   --idle-timeout 1m \
    #   --time-limit 9h \
    #   -- \
    #   --partition=${MY_PARTITION} \
    #   --account=${MY_GRANT_RES_CPU} \
    #   --mem-per-cpu=256M

    # Experiment with 2 CPU workers
    # Tried this out, however it allocated single-cpu workers anyway (as reported by `squeue`).
    # However HQ reported that each worker had two cores... Dunno, need more experimentation.
    # hq alloc add slurm \
    #   --workers-per-alloc 1 \
    #   --max-worker-count 48 \
    #   --backlog 36 \
    #   --idle-timeout 1m \
    #   --time-limit 9h \
    #   --cpus 2 \
    #   -- \
    #   --partition=${MY_PARTITION} \
    #   --account=${MY_GRANT_RES_CPU} \
    #   --mem-per-cpu=256M

    hq alloc add slurm \
      --workers-per-alloc 1 \
      --max-worker-count 4 \
      --backlog 4 \
      --idle-timeout 1m \
      --time-limit 5m \
      --cpus 2 \
      -- \
      --partition=${MY_PARTITION} \
      --account=${MY_GRANT_RES_CPU} \
      --mem-per-cpu=256M

  else
    echo "Seems that there are auto allocation queues present. Not starting another one."
    echo "You might want to run 'hq alloc list' and inspect your allocation queues."
  fi

}

assert_envvar_set MY_PARTITION
assert_envvar_set MY_GRANT
assert_envvar_set MY_GRANT_RES_CPU

# module load python/3.10.8-gcccore-12.2.0
# pip install -r requirements.txt
load_module_if_needed python/3.10.8-gcccore-12.2.0
pip install -r requirements.txt


# Had issues starting a server after a restrat with liberec
# module load hyperqueue/0.17.0-liberec
# module load hyperqueue/0.17.0
load_module_if_needed hyperqueue/0.17.0

start_hq_server_if_needed
create_auto_alloc_queue_if_needed


