"""Phase 3 pilot: choose the learning rate and the epoch on dev, and measure training noise.

Qwen2.5-1.5B-Instruct, cleaned arm, seed 1, all other settings the RunConfig defaults (decision 14,
length-grouped batches from decision 26). Two learning rates run in parallel, one per T4
(jobs/pilot.sh). Each is trained twice with the same seed, run a then run b on the same GPU, so
a against b shows how far a same-seed retrain repeats. After each training, dev is scored with
the adapter saved at the end of every epoch (greedy decoding, official scorer).

Selection rule, fixed on 16 Nov 2026 before any pilot result exists:
  For each (learning rate, epoch), take dev exe_correct averaged over runs a and b. Choose the
  highest. Ties go to fewer epochs, then to the lower learning rate. The main runs then use the
  same 3-epoch cosine schedule and are scored with the chosen epoch's adapter, so the schedule the
  pilot measured is the one the main runs train with.
The test split is never touched here.

Adapter weights and tokenizer copies are deleted after scoring (about 85 MB per epoch); the
weights' SHA-256 and the loss log are kept. Set KEEP_ADAPTERS=1 to keep everything.

Usage:
  python -m finqa_lora.pilot run --lr 1e-4 --rep a --out /kaggle/working/pilot   (one GPU)
  python -m finqa_lora.pilot report --out /kaggle/working/pilot
"""
import argparse
import hashlib
import json
import os
import shutil
import time
from pathlib import Path

MODEL = "Qwen/Qwen2.5-1.5B-Instruct"
SEED = 1
LEARNING_RATES = (1e-4, 2e-4)
REPS = ("a", "b")
RULE = ("highest dev exe_correct averaged over runs a and b; ties to fewer epochs, then the lower "
        "learning rate; main runs keep the 3-epoch cosine schedule and use that epoch's adapter")


def lr_name(lr):
    """1e-4 -> 'lr1e-4'. Folder names must not depend on float formatting quirks."""
    mantissa, exp = f"{lr:.0e}".split("e")
    return f"lr{mantissa}e{int(exp)}"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def epoch_checkpoints(train_dir):
    """checkpoint-<step> folders in step order. With save_strategy=epoch there is one per epoch."""
    found = [p for p in Path(train_dir).glob("checkpoint-*") if p.name.split("-")[1].isdigit()]
    return sorted(found, key=lambda p: int(p.name.split("-")[1]))


KEEP_FILES = ("trainer_state.json", "adapter_config.json")


def prune(train_dir):
    """Delete adapter weights and tokenizer copies (about 85 MB per epoch for the 1.5B model).

    Kept: train_metrics.json, and each checkpoint's trainer_state.json (loss log) and
    adapter_config.json. The weights' SHA-256 is already in result.json.
    """
    train_dir = Path(train_dir)
    shutil.rmtree(train_dir / "final", ignore_errors=True)
    for ckpt in epoch_checkpoints(train_dir):
        for f in ckpt.iterdir():
            if f.name not in KEEP_FILES:
                shutil.rmtree(f) if f.is_dir() else f.unlink()
    (train_dir / "README.md").unlink(missing_ok=True)


def run_one(lr, rep, out, model=MODEL, dev_limit=None, **overrides):
    """Train one configuration, score dev with each epoch's adapter, write <run>/result.json."""
    import gc

    import torch

    from finqa_lora.infer import run, write_rows
    from finqa_lora.train import RunConfig, train

    run_dir = Path(out) / lr_name(lr) / rep
    run_dir.mkdir(parents=True, exist_ok=True)
    cfg = RunConfig(model=model, arm="cleaned", seed=SEED, out=str(run_dir / "train"), learning_rate=lr,
                    **overrides)
    result = {"lr": lr, "rep": rep, "started": time.strftime("%Y-%m-%d %H:%M:%S"),
              "gpu": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
              "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES"), "dev_limit": dev_limit}
    metrics, trainer = train(cfg)
    del trainer
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    result["train"] = metrics
    result["epochs"] = []
    for epoch, ckpt in enumerate(epoch_checkpoints(cfg.out), 1):
        rows, summary = run(model, "dev", adapter=str(ckpt), limit=dev_limit)
        write_rows(rows, run_dir / f"dev_epoch{epoch}.csv")
        result["epochs"].append({"epoch": epoch, "step": int(ckpt.name.split("-")[1]),
                                 "adapter_sha256": sha256(ckpt / "adapter_model.safetensors"), **summary})
        print(f"{lr_name(lr)}/{rep} epoch {epoch}: dev exe_correct {summary['exe_correct']}/{summary['items']}",
              flush=True)
    if os.environ.get("KEEP_ADAPTERS") != "1":
        prune(cfg.out)
    result["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(run_dir / "result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    return result


def load_results(out):
    results = []
    for path in sorted(Path(out).glob("lr*/*/result.json")):
        with open(path, encoding="utf-8") as f:
            results.append(json.load(f))
    return results


def select(results):
    """Apply the selection rule. Returns the chosen config and the table it was chosen from."""
    table = {}
    for r in results:
        for e in r["epochs"]:
            table.setdefault((r["lr"], e["epoch"]), {})[r["rep"]] = e["exe_correct"]
    rows = [{"lr": lr, "epoch": ep, "by_rep": by_rep, "mean_exe_correct": sum(by_rep.values()) / len(by_rep),
             "complete": sorted(by_rep) == sorted(REPS)}
            for (lr, ep), by_rep in sorted(table.items())]
    if not rows:
        return None, rows
    best = min(rows, key=lambda r: (-r["mean_exe_correct"], r["epoch"], r["lr"]))
    return {"lr": best["lr"], "epoch": best["epoch"], "mean_exe_correct": best["mean_exe_correct"],
            "from_complete_pair": best["complete"]}, rows


def read_csv(path):
    import csv
    with open(path, encoding="utf-8") as f:
        return {r["id"]: r for r in csv.DictReader(f)}


def same_seed_noise(out, results):
    """Run a against run b, per learning rate and epoch: what a same-seed retrain changes."""
    by = {(r["lr"], r["rep"]): r for r in results}
    noise = {"training": [], "dev": []}
    for lr in sorted({r["lr"] for r in results}):
        a, b = by.get((lr, "a")), by.get((lr, "b"))
        if not (a and b):
            continue
        noise["training"].append({"lr": lr, "train_loss_a": a["train"]["train_loss"],
                                  "train_loss_b": b["train"]["train_loss"],
                                  "same_logged_losses": a["train"]["losses"] == b["train"]["losses"]})
        for ea, eb in zip(a["epochs"], b["epochs"]):
            ep = ea["epoch"]
            ra = read_csv(Path(out) / lr_name(lr) / "a" / f"dev_epoch{ep}.csv")
            rb = read_csv(Path(out) / lr_name(lr) / "b" / f"dev_epoch{ep}.csv")
            ids = sorted(ra.keys() & rb.keys())
            noise["dev"].append({
                "lr": lr, "epoch": ep, "items": len(ids),
                "same_adapter": ea["adapter_sha256"] == eb["adapter_sha256"],
                "exe_correct_a": ea["exe_correct"], "exe_correct_b": eb["exe_correct"],
                "same_reply": sum(ra[i]["reply"] == rb[i]["reply"] for i in ids),
                "right_in_a_only": sum(ra[i]["exe_correct"] == "1" and rb[i]["exe_correct"] == "0" for i in ids),
                "right_in_b_only": sum(ra[i]["exe_correct"] == "0" and rb[i]["exe_correct"] == "1" for i in ids),
            })
    return noise


def report(out):
    from finqa_lora.prompt import PROMPT_VERSION, prompt_fingerprint
    results = load_results(out)
    expected = [(lr, rep) for lr in LEARNING_RATES for rep in REPS]
    got = {(r["lr"], r["rep"]) for r in results}
    chosen, table = select(results)
    rep = {
        "written": time.strftime("%Y-%m-%d %H:%M:%S"),
        "prompt_version": PROMPT_VERSION, "prompt_fingerprint": prompt_fingerprint(),
        "rule": RULE,
        "missing_runs": [f"{lr_name(lr)}/{r}" for lr, r in expected if (lr, r) not in got],
        "chosen": chosen,
        "table": table,
        "same_seed_noise": same_seed_noise(out, results),
        "runs": [{"lr": r["lr"], "rep": r["rep"], "dev_limit": r["dev_limit"], "gpu": r["gpu"],
                  "train_seconds": r["train"]["seconds"], "seconds_per_step": r["train"]["seconds_per_step"],
                  "steps": r["train"]["steps"], "items": r["train"]["items"],
                  "train_loss": r["train"]["train_loss"], "loss_is_finite": r["train"]["loss_is_finite"],
                  "peak_gpu_gb": r["train"]["peak_gpu_gb"], "git_commit": r["train"]["git_commit"],
                  "sampling": r["train"]["config"]["sampling"],
                  "dev": [{"epoch": e["epoch"], "exe_correct": e["exe_correct"], "executes": e["executes"],
                           "seconds": e["seconds"]} for e in r["epochs"]]}
                 for r in results],
    }
    with open(Path(out) / "report.json", "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=2)
    return rep


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("--lr", type=float, required=True)
    r.add_argument("--rep", choices=REPS, required=True)
    r.add_argument("--out", required=True)
    r.add_argument("--model", default=MODEL)
    # For CPU dry runs with the tiny model only:
    r.add_argument("--dev-limit", type=int)
    r.add_argument("--subset", type=int, default=0)
    r.add_argument("--epochs", type=float, default=3.0)
    r.add_argument("--batch-size", type=int, default=8)
    r.add_argument("--grad-accum", type=int, default=2)
    s = sub.add_parser("report")
    s.add_argument("--out", required=True)
    a = p.parse_args()
    if a.cmd == "run":
        run_one(a.lr, a.rep, a.out, model=a.model, dev_limit=a.dev_limit, subset=a.subset, epochs=a.epochs,
                batch_size=a.batch_size, grad_accum=a.grad_accum)
    else:
        rep = report(a.out)
        print(json.dumps({k: rep[k] for k in ("missing_runs", "chosen", "table")}, indent=2))


if __name__ == "__main__":
    main()
