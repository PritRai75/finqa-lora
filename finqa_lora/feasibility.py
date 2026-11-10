"""Phase 2 feasibility job: measure each candidate model before choosing one.

For each candidate, in order (each step is recorded even if a later one fails):
  1. licence from the model card (Hugging Face Hub)
  2. token lengths of training examples and few-shot prompts with the real tokenizer
  3. base model on dev, zero-shot and few-shot (official scorer), then zero-shot again to measure
     how far greedy decoding on this GPU repeats itself
  4. a timed LoRA run on a random sample of the cleaned arm (fixed number of steps)
  5. extrapolated cost of one main run against the gate

The report is rewritten after every step: <out>/report.json. Predictions go to <out>/<model>/.
The test split is never touched here.

Usage: python -m finqa_lora.feasibility --out /kaggle/working/feasibility
"""
import argparse
import gc
import json
import platform
import time
import traceback
from pathlib import Path

import torch

from finqa_lora.data import load_split
from finqa_lora.infer import load_model, load_tokenizer, run, write_rows
from finqa_lora.prompt import PROMPT_VERSION, few_shot_examples, messages, prompt_fingerprint, target
from finqa_lora.train import RunConfig, arm_ids, chat_ids, git_commit, train

CANDIDATES = ("Qwen/Qwen2.5-1.5B-Instruct", "Qwen/Qwen3-4B-Instruct-2507")
GATE_HOURS = 2.5      # one main run: training plus dev scoring of each epoch's checkpoint
EPOCHS = 3
TIMED_STEPS = 30
TIMED_SUBSET = 640    # more than TIMED_STEPS x 16 so no example repeats


def pct(xs, p):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(p * (len(xs) - 1)))]


def token_stats(tok):
    train = load_split("train")
    by_id = {ex["id"]: ex for ex in train}
    lens = [len(chat_ids(tok, messages(by_id[i]) + [{"role": "assistant", "content": target(by_id[i])}]))
            for i in arm_ids("cleaned")]
    shots = few_shot_examples(train)
    few = [len(chat_ids(tok, messages(ex, shots), add_generation_prompt=True)) for ex in load_split("dev")]
    prog = [len(tok(target(ex), add_special_tokens=False)["input_ids"]) for ex in train]
    return {
        "train_example_tokens": {"median": pct(lens, .5), "p90": pct(lens, .9), "p99": pct(lens, .99),
                                 "max": max(lens), "total": sum(lens)},
        "dev_few_shot_prompt_tokens": {"median": pct(few, .5), "max": max(few)},
        "program_tokens_max": max(prog),
    }


def licence(model_id):
    try:
        from huggingface_hub import model_info
        info = model_info(model_id)
        return {"license": getattr(info.card_data, "license", None) if info.card_data else None,
                "gated": info.gated, "sha": info.sha}
    except Exception as e:
        return {"error": repr(e)}


def environment():
    env = {"python": platform.python_version(), "torch": torch.__version__,
           "cuda": torch.cuda.is_available(), "git_commit": git_commit()}
    if torch.cuda.is_available():
        env["gpu"] = torch.cuda.get_device_name(0)
        env["gpu_count"] = torch.cuda.device_count()
    for name in ("transformers", "peft", "trl", "accelerate", "datasets"):
        env[name] = __import__(name).__version__
    return env


def free_gpu():
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def timed_train(model_id, out, tok):
    """Short run at the main-run batch size; falls back to a smaller per-device batch on OOM."""
    for bs, accum in ((8, 2), (4, 4), (2, 8)):
        cfg = RunConfig(model=model_id, arm="cleaned", seed=1, out=str(out), batch_size=bs, grad_accum=accum,
                        max_steps=TIMED_STEPS, subset=TIMED_SUBSET, save=False)
        try:
            metrics, trainer = train(cfg, tok=tok)
            del trainer
            free_gpu()
            return metrics
        except torch.OutOfMemoryError:
            free_gpu()
            continue
    raise RuntimeError("out of memory even at per-device batch 2")


def evaluate_candidate(model_id, out, report, save, candidates=None):
    key = model_id
    r = report["candidates"].setdefault(key, {})
    mdir = out / model_id.replace("/", "__")

    def step(name, fn):
        t0 = time.time()
        try:
            r[name] = fn()
        except Exception as e:
            r[name] = {"error": repr(e), "traceback": traceback.format_exc()[-3000:]}
        r.setdefault("step_seconds", {})[name] = round(time.time() - t0, 1)
        save()

    step("licence", lambda: licence(model_id))
    tok = load_tokenizer(model_id)
    step("tokens", lambda: token_stats(tok))
    model = load_model(model_id)

    def base(shots, name):
        rows, summary = run(model_id, "dev", shots=shots, model=model, tok=tok, batch_size=16)
        write_rows(rows, mdir / f"dev_base_{name}.csv")
        return rows, summary

    first = {}

    def zero():
        first["rows"], summary = base(0, "0shot")
        return summary

    def repeat():
        rows, summary = base(0, "0shot_repeat")
        a = first["rows"]
        return summary | {
            "same_reply": sum(x["reply"] == y["reply"] for x, y in zip(a, rows)),
            "same_exe_correct": sum(x["exe_correct"] == y["exe_correct"] for x, y in zip(a, rows)),
            "changed_ids": [x["id"] for x, y in zip(a, rows) if x["reply"] != y["reply"]][:50],
        }

    step("dev_zero_shot", zero)
    step("dev_few_shot", lambda: base(4, "4shot")[1])
    step("dev_zero_shot_repeat", repeat)
    del model
    free_gpu()
    step("timed_train", lambda: timed_train(model_id, mdir / "timed_run", load_tokenizer(model_id)))

    def estimate():
        t = r["timed_train"]
        dev_s = r["dev_zero_shot"]["seconds"]
        n = report["arm_items"]
        steps_per_epoch = -(-n // t["examples_per_step"])
        train_h = t["seconds_per_step"] * steps_per_epoch * EPOCHS / 3600
        dev_h = dev_s * EPOCHS / 3600
        return {"steps_per_epoch": steps_per_epoch, "train_hours": round(train_h, 2),
                "dev_scoring_hours": round(dev_h, 2), "total_hours": round(train_h + dev_h, 2),
                "passes_gate": train_h + dev_h <= GATE_HOURS, "gate_hours": GATE_HOURS, "epochs": EPOCHS}

    step("estimate", estimate)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--models", nargs="+", default=list(CANDIDATES))
    a = p.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    report = {"started": time.strftime("%Y-%m-%d %H:%M:%S"), "environment": environment(),
              "prompt_version": PROMPT_VERSION, "prompt_fingerprint": prompt_fingerprint(),
              "arm_items": len(arm_ids("cleaned")), "candidates": {}}

    def save():
        with open(out / "report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, default=str)

    save()
    for model_id in a.models:
        print(f"=== {model_id}", flush=True)
        try:
            evaluate_candidate(model_id, out, report, save)
        except Exception as e:  # e.g. the model cannot be downloaded or loaded
            report["candidates"].setdefault(model_id, {})["fatal"] = {
                "error": repr(e), "traceback": traceback.format_exc()[-3000:]}
            save()
        free_gpu()
    report["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    save()
    print(json.dumps({m: {k: v for k, v in c.items() if k in ("dev_zero_shot", "dev_few_shot", "dev_zero_shot_repeat", "estimate")}
                      for m, c in report["candidates"].items()}, indent=2, default=str))


if __name__ == "__main__":
    main()
