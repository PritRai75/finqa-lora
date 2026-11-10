#!/usr/bin/env bash
# Feasibility run 2: licence, token counts and the timed LoRA run for both candidates, plus the
# cost estimate. Dev baselines are carried over from run 1 instead of being measured again.
set -euo pipefail
python -m finqa_lora.feasibility --out "$1" --only licence tokens timed_train estimate \
    --previous results/feasibility/run1/report.json ${MODELS:+--models $MODELS}
