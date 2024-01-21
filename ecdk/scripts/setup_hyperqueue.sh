#!/usr/bin/bash

module load python/3.10.8-gcccore-12.2.0
pip install -r requirements.txt

module load hyperqueue/0.17.0

nohup hq server start &

# Enable automatic allocation (create queue)
hq alloc add slurm \
  --time-limit 2h \
  --workers-per-alloc 1 \
  --max-worker-count 36 \
  --backlog 36 \
  --idle-timeout 5m \
  -- \
  --partition=plgrid \
  --account=plglscclass23-cpu \
  --mail-type=begin \
  --mail-type=end \
  --mail-user=kkafara@student.agh.edu.pl

