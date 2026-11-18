#!/usr/bin/env bash
# Main runs (phase 4): cleaned versus random at the learning rate and epoch the pilot chose (read from
# the committed results/pilot/run1/report.json; the job stops if it is missing). MAIN_JOB picks the
# seeds: "main" (default) runs seeds 1 to 3, "main2" seeds 4 and 5 (jobs/main2.sh). Two chains in
# parallel, one per T4, read from finqa_lora.mainruns.JOBS; each slot pairs the two arms of one seed.
# Adapters are kept in <out>/<arm>/seed<k>/adapter/ for the test passes. Output dir is $1.
# Session time per slot: training to the chosen epoch + one dev pass, about 1.55 h (pilot, 16 Nov).
# Each GPU's output goes to its own log: <out>/gpu0.log and <out>/gpu1.log.
# CPU dry runs only: MAIN_ARGS is passed to every "mainruns run", PILOT_REPORT points at another pilot
# report, REQUIRE_GPUS=0 skips the GPU check. None of them is set on Kaggle.
set -uo pipefail
OUT="$1"
MAIN_JOB="${MAIN_JOB:-main}"
mkdir -p "$OUT"

PILOT=(${PILOT_REPORT:+--pilot-report "$PILOT_REPORT"})

python - <<EOF || exit 1
import os, torch
from finqa_lora.mainruns import PILOT_REPORT, frozen
n = torch.cuda.device_count()
need = int("${REQUIRE_GPUS:-2}")
print(f"GPUs visible: {n}, needed: {need}")
if n < need:
    raise SystemExit("The main runs use one chain per GPU. Settings > Accelerator > GPU T4 x2.")
print("frozen config:", frozen(os.environ.get("PILOT_REPORT") or PILOT_REPORT))
EOF

chain() {  # <gpu> <arm:seed> ...: run each in turn; stop this GPU's chain at the first error
    local gpu="$1"
    shift
    for job in "$@"; do
        echo "$(date '+%F %T') start ${job%%:*} seed ${job##*:} on GPU $gpu"
        CUDA_VISIBLE_DEVICES="$gpu" python -m finqa_lora.mainruns run --arm "${job%%:*}" --seed "${job##*:}" \
            --out "$OUT" "${PILOT[@]}" ${MAIN_ARGS:-} || return 1
        echo "$(date '+%F %T') done ${job%%:*} seed ${job##*:}"
    done
}

C0=$(python -m finqa_lora.mainruns chain --job "$MAIN_JOB" --gpu 0) || exit 1
C1=$(python -m finqa_lora.mainruns chain --job "$MAIN_JOB" --gpu 1) || exit 1
echo "job $MAIN_JOB: GPU 0 runs $C0; GPU 1 runs $C1"
# $C0 and $C1 are unquoted on purpose: one word per run.
chain 0 $C0 > "$OUT/gpu0.log" 2>&1 &
P0=$!
chain 1 $C1 > "$OUT/gpu1.log" 2>&1 &
P1=$!
echo "started: GPU 0 (pid $P0), GPU 1 (pid $P1). Progress: $OUT/gpu0.log, $OUT/gpu1.log"

FAILED=0
for pair in "0:$P0" "1:$P1"; do
    gpu="${pair%%:*}"
    if wait "${pair#*:}"; then
        echo "GPU $gpu chain finished"
    else
        echo "GPU $gpu chain FAILED. Last lines of its log:"
        tail -n 40 "$OUT/gpu$gpu.log"
        FAILED=1
    fi
done

# The report is written even if a chain failed: it lists the missing runs.
python -m finqa_lora.mainruns report --out "$OUT" --job "$MAIN_JOB" "${PILOT[@]}" || FAILED=1
exit "$FAILED"
