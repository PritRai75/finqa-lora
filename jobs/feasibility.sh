#!/usr/bin/env bash
# Feasibility run 1 (10 Nov 2026): every step for both candidates. Output dir is $1.
set -euo pipefail
python -m finqa_lora.feasibility --out "$1" ${MODELS:+--models $MODELS}
