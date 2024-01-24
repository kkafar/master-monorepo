#!/usr/bin/bash

module load python/3.10.8-gcccore-12.2.0
pip install -r requirements.txt

# Had issues starting a server after a restrat with liberec
# module load hyperqueue/0.17.0-liberec
module load hyperqueue/0.17.0

nohup hq server start &

# Enable automatic allocation (create queue)
hq alloc add slurm \
  --time-limit 5h \
  --workers-per-alloc 1 \
  --max-worker-count 48 \
  --backlog 36 \
  --idle-timeout 1m \
  -- \
  --partition=plgrid \
  --account=plglscclass23-cpu \
  --mem-per-cpu=256M \
  --mail-type=begin \
  --mail-type=end \
  --mail-user=kkafara@student.agh.edu.pl

