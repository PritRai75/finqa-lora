#!/usr/bin/env bash
# Main runs (phase 4): cleaned versus random, seeds 1 to 3, at the learning rate and epoch the pilot
# chose (read from the committed results/pilot/run1/report.json; the job stops if it is missing).
# Two chains in parallel, one per T4; each slot pairs the two arms of one seed (finqa_lora/mainruns.py).
# Adapters are kept in <out>/<arm>/seed<k>/adapter/ for the test passes. Output dir is $1.
# Session time: about 3 x (training to the chosen epoch + one dev pass); see the S4 handoff.
# Each GPU's output goes to its own log: <out>/gpu0.log and <out>/gpu1.log.
# CPU dry runs only: MAIN_ARGS is passed to every "mainruns run", PILOT_REPORT points at another pilot
# report, REQUIRE_GPUS=0 skips the GPU check. None of them is set on Kaggle.
set -uo pipefail
OUT="$1"
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

# Must match mainruns.CHAINS (a test checks this).
chain 0 cleaned:1 random:2 cleaned:3 > "$OUT/gpu0.log" 2>&1 &
P0=$!
chain 1 random:1 cleaned:2 random:3 > "$OUT/gpu1.log" 2>&1 &
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
python -m finqa_lora.mainruns report --out "$OUT" "${PILOT[@]}" || FAILED=1
exit "$FAILED"
