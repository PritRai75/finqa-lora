"""Phase 4 main runs: cleaned versus random, 3 seeds each, at the configuration the pilot chose.

Learning rate and epoch are read from the committed pilot record (results/pilot/run1/report.json),
chosen there by the rule fixed before the pilot (decision 32). Nothing else changes from the pilot:
same model, prompt, LoRA settings and 3-epoch cosine schedule. Training stops at the end of the
chosen epoch (train.StopAfterEpoch), so the schedule up to that point is the one the pilot measured.

Arms (decision 5): cleaned = train minus the 431 screen flags; random = the same number of items
drawn from all of train with ARM_SEED. Seeds 1, 2, 3. Seed 1 of the cleaned arm repeats the pilot's
runs a and b at the chosen setting, which gives one more same-seed comparison for free.

jobs/main.sh runs two chains in parallel, one per T4. Each slot pairs the two arms of one seed, one
arm per GPU, so a job cut short still leaves complete seed pairs:
  slot 1: GPU 0 cleaned seed 1, GPU 1 random seed 1
  slot 2: GPU 0 random seed 2,  GPU 1 cleaned seed 2
  slot 3: GPU 0 cleaned seed 3, GPU 1 random seed 3

Each run keeps its adapter (about 74 MB) in <arm>/seed<k>/adapter/ for the test passes, scores dev
once with it, and deletes everything else heavy. Test is not touched here.

Usage:
  python -m finqa_lora.mainruns run --arm cleaned --seed 1 --out /kaggle/working/main   (one GPU)
  python -m finqa_lora.mainruns report --out /kaggle/working/main
"""
import argparse
import json
import os
import shutil
import time
from pathlib import Path

from finqa_lora import REPO_ROOT
from finqa_lora.pilot import MODEL, epoch_checkpoints, lr_name, prune, sha256

ARMS = ("cleaned", "random")
SEEDS = (1, 2, 3)
SCHEDULE_EPOCHS = 3.0
PILOT_REPORT = REPO_ROOT / "results" / "pilot" / "run1" / "report.json"
CHAINS = {0: [("cleaned", 1), ("random", 2), ("cleaned", 3)],
          1: [("random", 1), ("cleaned", 2), ("random", 3)]}
ADAPTER_FILES = ("adapter_model.safetensors", "adapter_config.json")


def frozen(report_path=PILOT_REPORT):
    """The learning rate and epoch chosen by the pilot. Refuses an incomplete or missing pilot."""
    report_path = Path(report_path)
    if not report_path.exists():
        raise SystemExit(f"{report_path} is missing: commit the pilot record before the main runs")
    with open(report_path, encoding="utf-8") as f:
        rep = json.load(f)
    chosen = rep.get("chosen")
    if rep.get("missing_runs") or not chosen or not chosen.get("from_complete_pair"):
        raise SystemExit(f"{report_path}: the pilot is incomplete (missing {rep.get('missing_runs')}); "
                         "the selection rule needs both runs of every learning rate")
    return {"lr": chosen["lr"], "epoch": int(chosen["epoch"]), "pilot_mean_dev_exe_correct": chosen["mean_exe_correct"],
            "pilot_report": report_path.as_posix(), "pilot_report_written": rep.get("written"),
            "prompt_fingerprint": rep.get("prompt_fingerprint")}


def run_dir(out, arm, seed):
    return Path(out) / arm / f"seed{seed}"


def run_one(arm, seed, out, model=MODEL, dev_limit=None, report_path=PILOT_REPORT, **overrides):
    """Train one arm and seed to the chosen epoch, keep the adapter, score dev, write result.json."""
    import gc

    import torch

    from finqa_lora.infer import run, write_rows
    from finqa_lora.prompt import prompt_fingerprint
    from finqa_lora.train import RunConfig, train

    if arm not in ARMS:
        raise ValueError(f"unknown arm {arm!r}")
    fz = frozen(report_path)
    if fz["prompt_fingerprint"] and fz["prompt_fingerprint"] != prompt_fingerprint():
        raise SystemExit(f"prompt changed since the pilot ({fz['prompt_fingerprint']} -> {prompt_fingerprint()})")
    d = run_dir(out, arm, seed)
    d.mkdir(parents=True, exist_ok=True)
    cfg = RunConfig(model=model, arm=arm, seed=seed, out=str(d / "train"), learning_rate=fz["lr"],
                    epochs=overrides.pop("epochs", SCHEDULE_EPOCHS), stop_after_epoch=fz["epoch"], **overrides)
    result = {"arm": arm, "seed": seed, "lr": fz["lr"], "epoch": fz["epoch"], "frozen_from": fz,
              "started": time.strftime("%Y-%m-%d %H:%M:%S"),
              "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
              "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"), "dev_limit": dev_limit}
    metrics, trainer = train(cfg)
    del trainer
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    result["train"] = metrics

    ckpts = epoch_checkpoints(cfg.out)
    if len(ckpts) != fz["epoch"]:
        raise RuntimeError(f"expected {fz['epoch']} epoch checkpoints, found {[c.name for c in ckpts]}")
    last = ckpts[-1]
    adapter = d / "adapter"
    adapter.mkdir(exist_ok=True)
    for name in ADAPTER_FILES:
        shutil.copy2(last / name, adapter / name)
    final = Path(cfg.out) / "final" / "adapter_model.safetensors"
    result["adapter_sha256"] = sha256(adapter / "adapter_model.safetensors")
    result["adapter_bytes"] = (adapter / "adapter_model.safetensors").stat().st_size
    result["step"] = int(last.name.split("-")[1])
    # The adapter saved when training stopped must be the chosen epoch's checkpoint.
    result["final_is_chosen_epoch"] = final.exists() and sha256(final) == result["adapter_sha256"]
    prune(cfg.out)

    rows, summary = run(model, "dev", adapter=str(adapter), limit=dev_limit)
    write_rows(rows, d / "dev.csv")
    result["dev"] = summary
    result["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(d / "result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print(f"{arm}/seed{seed}: epoch {fz['epoch']} (step {result['step']}), dev exe_correct "
          f"{summary['exe_correct']}/{summary['items']}", flush=True)
    return result


def load_results(out):
    results = []
    for path in sorted(Path(out).glob("*/seed*/result.json")):
        with open(path, encoding="utf-8") as f:
            results.append(json.load(f))
    return results


def pilot_repeat(result, report_path):
    """Cleaned seed 1 against the pilot's runs a and b at the chosen learning rate and epoch."""
    folder = Path(report_path).parent / lr_name(result["lr"])
    out = {}
    for rep in ("a", "b"):
        path = folder / rep / "result.json"
        if not path.exists():
            continue
        with open(path, encoding="utf-8") as f:
            pilot = json.load(f)
        e = next((e for e in pilot["epochs"] if e["epoch"] == result["epoch"]), None)
        if e:
            out[rep] = {"dev_exe_correct": e["exe_correct"], "same_adapter": e["adapter_sha256"] == result["adapter_sha256"]}
    return out


def report(out, report_path=PILOT_REPORT):
    results = load_results(out)
    got = {(r["arm"], r["seed"]) for r in results}
    rep = {
        "written": time.strftime("%Y-%m-%d %H:%M:%S"),
        "frozen": frozen(report_path),
        "missing_runs": [f"{a}/seed{s}" for s in SEEDS for a in ARMS if (a, s) not in got],
        "complete_seed_pairs": [s for s in SEEDS if all((a, s) in got for a in ARMS)],
        "dev": {f"{r['arm']}/seed{r['seed']}": {"exe_correct": r["dev"]["exe_correct"], "items": r["dev"]["items"],
                                                 "executes": r["dev"]["executes"]} for r in results},
        "cleaned_seed1_vs_pilot": next((pilot_repeat(r, report_path) for r in results
                                        if r["arm"] == "cleaned" and r["seed"] == 1), None),
        "runs": [{"arm": r["arm"], "seed": r["seed"], "gpu": r["gpu"], "step": r["step"], "items": r["train"]["items"],
                  "dropped_over_max_length": len(r["train"]["dropped_over_max_length"]),
                  "train_seconds": r["train"]["seconds"], "seconds_per_step": r["train"]["seconds_per_step"],
                  "train_loss": r["train"]["train_loss"], "loss_is_finite": r["train"]["loss_is_finite"],
                  "last_learning_rate": (r["train"].get("learning_rates") or [None])[-1],
                  "peak_gpu_gb": r["train"]["peak_gpu_gb"], "dev_seconds": r["dev"]["seconds"],
                  "adapter_sha256": r["adapter_sha256"], "adapter_bytes": r["adapter_bytes"],
                  "final_is_chosen_epoch": r["final_is_chosen_epoch"], "git_commit": r["train"]["git_commit"]}
                 for r in results],
    }
    with open(Path(out) / "report.json", "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=2)
    return rep


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--arm", choices=ARMS, required=True)
    r.add_argument("--seed", type=int, choices=SEEDS, required=True)
    r.add_argument("--out", required=True)
    r.add_argument("--model", default=MODEL)
    r.add_argument("--pilot-report", default=PILOT_REPORT)
    # For CPU dry runs with the tiny model only:
    r.add_argument("--dev-limit", type=int)
    r.add_argument("--subset", type=int, default=0)
    r.add_argument("--epochs", type=float, default=SCHEDULE_EPOCHS)
    r.add_argument("--batch-size", type=int, default=8)
    r.add_argument("--grad-accum", type=int, default=2)
    s = sub.add_parser("report")
    s.add_argument("--out", required=True)
    s.add_argument("--pilot-report", default=PILOT_REPORT)
    a = p.parse_args()
    if a.cmd == "run":
        run_one(a.arm, a.seed, a.out, model=a.model, dev_limit=a.dev_limit, report_path=a.pilot_report,
                subset=a.subset, epochs=a.epochs, batch_size=a.batch_size, grad_accum=a.grad_accum)
    else:
        rep = report(a.out, a.pilot_report)
        print(json.dumps({k: rep[k] for k in ("frozen", "missing_runs", "dev", "cleaned_seed1_vs_pilot")}, indent=2))


if __name__ == "__main__":
    main()
