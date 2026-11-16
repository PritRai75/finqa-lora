#!/usr/bin/env bash
# Pilot (phase 3, decision 26): learning rate 1e-4 on GPU 0 and 2e-4 on GPU 1, in parallel. Each
# GPU trains its rate twice with seed 1 (runs a, then b) and scores dev after every epoch.
# Then report.json applies the selection rule in finqa_lora/pilot.py. Output dir is $1.
# Session time about 3.5 to 4.5 h (estimate from feasibility run 2). Needs GPU T4 x2.
# Each GPU's output goes to its own log: <out>/gpu0.log and <out>/gpu1.log.
# PILOT_ARGS (CPU dry runs only) is passed to every "pilot run"; REQUIRE_GPUS=0 skips the GPU check.
set -uo pipefail
OUT="$1"
mkdir -p "$OUT"

python - <<EOF || exit 1
import torch
n = torch.cuda.device_count()
need = int("${REQUIRE_GPUS:-2}")
print(f"GPUs visible: {n}, needed: {need}")
if n < need:
    raise SystemExit("The pilot runs one learning rate per GPU. Settings > Accelerator > GPU T4 x2.")
EOF

chain() {  # <gpu> <learning rate>: run a, then run b; stop this GPU's chain at the first error
    for rep in a b; do
        echo "$(date '+%F %T') start lr $2 run $rep on GPU $1"
        CUDA_VISIBLE_DEVICES="$1" python -m finqa_lora.pilot run --lr "$2" --rep "$rep" --out "$OUT" \
            ${PILOT_ARGS:-} || return 1
        echo "$(date '+%F %T') done lr $2 run $rep"
    done
}

chain 0 1e-4 > "$OUT/gpu0.log" 2>&1 &
P0=$!
chain 1 2e-4 > "$OUT/gpu1.log" 2>&1 &
P1=$!
echo "started: GPU 0 lr 1e-4 (pid $P0), GPU 1 lr 2e-4 (pid $P1). Progress: $OUT/gpu0.log, $OUT/gpu1.log"

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

# The report is written even if one chain failed: it lists the missing runs.
python -m finqa_lora.pilot report --out "$OUT" || FAILED=1
exit "$FAILED"
