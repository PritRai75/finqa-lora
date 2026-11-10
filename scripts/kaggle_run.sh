#!/usr/bin/env bash
# Run one job from jobs/ on a Kaggle GPU machine. Stops at the first failing command.
# Usage (from the repo root): bash scripts/kaggle_run.sh <job name> <output dir>
set -euo pipefail
JOB="$1"
OUT="$2"
mkdir -p "$OUT"
echo "commit $(git rev-parse HEAD)  $(git log -1 --format=%s)"
# Kaggle preinstalls torchao 0.10; PEFT refuses any torchao older than 0.16 even though
# nothing here uses it (feasibility run 1, 10 Nov 2026). Remove it.
pip uninstall -y -q torchao 2>/dev/null || true
pip install -q -r requirements-gpu.txt
python -m finqa_lora.fetch
pip freeze > "$OUT/pip-freeze.txt"
# One GPU only: with two visible, the Hugging Face Trainer switches to DataParallel.
export CUDA_VISIBLE_DEVICES=0
bash "jobs/$JOB.sh" "$OUT" 2>&1 | tee "$OUT/$JOB.log"
