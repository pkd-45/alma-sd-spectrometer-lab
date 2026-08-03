#!/bin/bash
#SBATCH --job-name=alma-sd-demo
#SBATCH --cpus-per-task=4
#SBATCH --mem=4G
#SBATCH --time=00:15:00
#SBATCH --output=logs/%x-%j.out

set -euo pipefail
mkdir -p logs products
python -m alma_lab demo --workers "${SLURM_CPUS_PER_TASK}" --output "products/slurm-${SLURM_JOB_ID}"
