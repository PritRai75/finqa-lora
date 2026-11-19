#!/usr/bin/env bash
# Test passes (phase 4): the 10 main-run adapters and the three prompted base models on the test split,
# once, after check2 and check3 are committed (finqa_lora/testpass.py has the full plan).
# Order, each step stopping the job if it fails, so test is touched only after every check passed:
#   1. the test gate is open (python -m finqa_lora.testgate)
#   2. all 10 adapters are found under $ADAPTERS by the SHA-256 in the committed reports
#   3. one dev check per GPU repeats the committed dev replies within decision 38's tolerance
#   4. two chains of test passes, one per T4; each GPU's output goes to <out>/gpu0.log, <out>/gpu1.log
# ADAPTERS: where the adapter dataset is mounted (default /kaggle/input, searched recursively).
# CPU dry runs only: TESTPASS_ARGS is passed to every devcheck and run (--model, --limit, --results),
# LOCATE_ARGS to locate (--results), REQUIRE_GPUS=0 skips the GPU check. None is set on Kaggle.
# Session time (estimate): about 1 h; GPU 0 about 54 min, GPU 1 about 46 min (dev timings x 1.3).
set -uo pipefail
OUT="$1"
ADAPTERS="${ADAPTERS:-/kaggle/input}"
mkdir -p "$OUT"

python -m finqa_lora.testgate || { echo "test gate closed: nothing was run"; exit 1; }

python - <<EOF || exit 1
import torch
n = torch.cuda.device_count()
need = int("${REQUIRE_GPUS:-2}")
print(f"GPUs visible: {n}, needed: {need}")
if n < need:
    raise SystemExit("The test passes use one chain per GPU. Settings > Accelerator > GPU T4 x2.")
EOF

python -m finqa_lora.testpass locate --adapters "$ADAPTERS" ${LOCATE_ARGS:-} || exit 1

# Separate copy folders per GPU, so the two processes never write the same file.
CUDA_VISIBLE_DEVICES=0 python -m finqa_lora.testpass devcheck --gpu 0 --adapters "$ADAPTERS" --out "$OUT" \
    --work /tmp/testpass-adapters/gpu0 ${TESTPASS_ARGS:-} > "$OUT/devcheck-gpu0.log" 2>&1 &
D0=$!
CUDA_VISIBLE_DEVICES=1 python -m finqa_lora.testpass devcheck --gpu 1 --adapters "$ADAPTERS" --out "$OUT" \
    --work /tmp/testpass-adapters/gpu1 ${TESTPASS_ARGS:-} > "$OUT/devcheck-gpu1.log" 2>&1 &
D1=$!
FAILED=0
for pair in "0:$D0" "1:$D1"; do
    if ! wait "${pair#*:}"; then
        echo "dev check on GPU ${pair%%:*} FAILED: test not touched. Last lines of its log:"
        tail -n 20 "$OUT/devcheck-gpu${pair%%:*}.log"
        FAILED=1
    fi
done
grep -h "^dev check" "$OUT"/devcheck-gpu*.log
[ "$FAILED" = 0 ] || exit 1

chain() {  # <gpu> <pass> ...: run each in turn; stop this GPU's chain at the first error
    local gpu="$1"
    shift
    for name in "$@"; do
        echo "$(date '+%F %T') start $name on GPU $gpu"
        CUDA_VISIBLE_DEVICES="$gpu" python -m finqa_lora.testpass run --pass "$name" --adapters "$ADAPTERS" \
            --out "$OUT" --work "/tmp/testpass-adapters/gpu$gpu" ${TESTPASS_ARGS:-} || return 1
        echo "$(date '+%F %T') done $name"
    done
}

C0=$(python -m finqa_lora.testpass chain --gpu 0) || exit 1
C1=$(python -m finqa_lora.testpass chain --gpu 1) || exit 1
echo "GPU 0 runs:" $C0
echo "GPU 1 runs:" $C1
# $C0 and $C1 are unquoted on purpose: one word per pass.
chain 0 $C0 > "$OUT/gpu0.log" 2>&1 &
P0=$!
chain 1 $C1 > "$OUT/gpu1.log" 2>&1 &
P1=$!
echo "started: GPU 0 (pid $P0), GPU 1 (pid $P1). Progress: $OUT/gpu0.log, $OUT/gpu1.log"

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

# The report is written even if a chain failed: it lists the missing passes.
python -m finqa_lora.testpass report --out "$OUT" || FAILED=1
exit "$FAILED"
