# !/bin/bash
#!/usr/bin/bash

function assert_envvar_set() {
  cmdname=$1
  if [ -z "${!cmdname}" ]; then
      echo "$cmdname is unset or set to the empty string"
      exit 1
  fi
}

assert_envvar_set MY_PARTITION
assert_envvar_set MY_GRANT
assert_envvar_set MY_GRANT_RES_CPU

exit 0

module load python/3.10.8-gcccore-12.2.0
pip install -r requirements.txt

# Had issues starting a server after a restrat with liberec
# module load hyperqueue/0.17.0-liberec
module load hyperqueue/0.17.0

nohup hq server start &

# Let the server start
sleep 5

# Enable automatic allocation (create queue)
hq alloc add slurm \
  --time-limit 5h \
  --workers-per-alloc 1 \
  --max-worker-count 48 \
  --backlog 36 \
  --idle-timeout 1m \
  -- \
  --partition=${MY_PARTITION} \
  --account=${MY_GRANT_RES_CPU} \
  --mem-per-cpu=256M

