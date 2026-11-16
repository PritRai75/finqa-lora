#!/usr/bin/env bash
# Feasibility run 1 (10 Nov 2026): every step for both candidates. Output dir is $1.
set -euo pipefail
# One GPU only: with two visible, the Hugging Face Trainer switches to DataParallel.
export CUDA_VISIBLE_DEVICES=0
python -m finqa_lora.feasibility --out "$1" ${MODELS:+--models $MODELS}
