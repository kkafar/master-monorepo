#!/usr/bin/env python3
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --partition=plgrid
#SBATCH --time=00:01:00
#SBATCH --account=plglscclass23-cpu

import sys
import os
version_major = sys.version_info.major
version_minor = sys.version_info.minor
version_micro = sys.version_info.micro

print("Python %d.%d.%d" % (version_major, version_minor, version_micro))
print(f"cwd: {os.getcwd()}")

