#!/usr/bin/env bash
# Main runs, seeds 4 and 5 (decision 40): jobs/main.sh with the "main2" chains from
# finqa_lora.mainruns.JOBS. Output dir is $1; record it as results/main/run2/.
MAIN_JOB=main2 exec bash "$(dirname "$0")/main.sh" "$@"
