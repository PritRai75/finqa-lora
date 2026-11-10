"""LoRA supervised fine-tuning with TRL's SFTTrainer.

Loss is on the program (the completion) only. Prompts are built by finqa_lora.prompt, the same
function inference uses. One checkpoint is saved per epoch so the epoch can be chosen on dev.

Arms (from the screen in results/screen/train.csv):
  cleaned  train minus every `disagree` item (5,820 items with parser v1)
  random   the same number of items drawn at random from all 6,251 (seed ARM_SEED)

Usage (GPU): python -m finqa_lora.train --model Qwen/Qwen2.5-1.5B-Instruct --arm cleaned --seed 1 --out runs/x
"""
import argparse
import csv
import dataclasses
import hashlib
import json
import random
import subprocess
import time
from pathlib import Path

import torch
from datasets import Dataset
from peft import LoraConfig
from transformers import AutoModelForCausalLM, TrainerCallback
from trl import SFTConfig, SFTTrainer

from finqa_lora import REPO_ROOT
from finqa_lora.data import load_split
from finqa_lora.infer import device_and_dtype, load_tokenizer
from finqa_lora.prompt import PROMPT_VERSION, messages, prompt_fingerprint, target

ARM_SEED = 20261103


@dataclasses.dataclass
class RunConfig:
    model: str
    arm: str = "cleaned"
    seed: int = 1
    out: str = "runs/run"
    lora_r: int = 16
    lora_alpha: int = 32
    lora_dropout: float = 0.05
    learning_rate: float = 2e-4
    epochs: float = 3.0
    batch_size: int = 8
    grad_accum: int = 2
    max_length: int = 1024
    warmup_ratio: float = 0.03
    max_steps: int = -1          # > 0 only for timing runs
    subset: int = 0              # > 0 keeps only the first N arm items (timing runs)
    save: bool = True


def screen_status():
    with open(REPO_ROOT / "results" / "screen" / "train.csv", encoding="utf-8") as f:
        return {r["id"]: r["status"] for r in csv.DictReader(f)}


def arm_ids(arm):
    status = screen_status()
    all_ids = sorted(status)
    cleaned = [i for i in all_ids if status[i] != "disagree"]
    if arm == "cleaned":
        return cleaned
    if arm == "random":
        return sorted(random.Random(ARM_SEED).sample(all_ids, len(cleaned)))
    raise ValueError(f"unknown arm {arm!r}")


def chat_ids(tok, msgs, **kw):
    """Token ids of a chat. apply_chat_template returns a BatchEncoding in transformers 5."""
    enc = tok.apply_chat_template(msgs, tokenize=True, **kw)
    return list(enc["input_ids"] if hasattr(enc, "keys") else enc)


def build_dataset(ids, tok, max_length):
    by_id = {ex["id"]: ex for ex in load_split("train")}
    rows, dropped = [], []
    for i in ids:
        ex = by_id[i]
        prompt = messages(ex)
        completion = [{"role": "assistant", "content": target(ex)}]
        if len(chat_ids(tok, prompt + completion)) > max_length:
            dropped.append(i)  # never truncate: a cut program teaches the wrong answer
            continue
        rows.append({"prompt": prompt, "completion": completion})
    return Dataset.from_list(rows), dropped


class StepTimer(TrainerCallback):
    def __init__(self):
        self.times = []

    def on_step_end(self, args, state, control, **kw):
        self.times.append(time.time())


def git_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True,
                                       stderr=subprocess.DEVNULL).strip()
    except Exception:
        return "unknown"


def train(cfg: RunConfig, model=None, tok=None):
    out = Path(cfg.out)
    out.mkdir(parents=True, exist_ok=True)
    device, dtype = device_and_dtype()
    tok = tok or load_tokenizer(cfg.model)
    tok.padding_side = "right"
    ids = arm_ids(cfg.arm)
    if cfg.subset:
        ids = sorted(random.Random(cfg.seed).sample(ids, cfg.subset))
    ds, dropped = build_dataset(ids, tok, cfg.max_length)
    model = model or AutoModelForCausalLM.from_pretrained(cfg.model, dtype=dtype).to(device)
    args = SFTConfig(
        output_dir=str(out),
        per_device_train_batch_size=cfg.batch_size,
        gradient_accumulation_steps=cfg.grad_accum,
        learning_rate=cfg.learning_rate,
        num_train_epochs=cfg.epochs,
        max_steps=cfg.max_steps,
        lr_scheduler_type="cosine",
        warmup_steps=cfg.warmup_ratio,  # TRL/transformers treat a float < 1 as a ratio
        max_length=cfg.max_length,
        completion_only_loss=True,
        gradient_checkpointing=device == "cuda",
        fp16=device == "cuda",
        logging_steps=10,
        save_strategy="epoch" if cfg.save else "no",
        save_only_model=True,
        report_to="none",
        seed=cfg.seed,
        data_seed=cfg.seed,
        use_cpu=device == "cpu",
    )
    peft_cfg = LoraConfig(r=cfg.lora_r, lora_alpha=cfg.lora_alpha, lora_dropout=cfg.lora_dropout,
                          target_modules="all-linear", task_type="CAUSAL_LM")
    timer = StepTimer()
    trainer = SFTTrainer(model=model, args=args, train_dataset=ds, processing_class=tok,
                         peft_config=peft_cfg, callbacks=[timer])
    trainable = sum(p.numel() for p in trainer.model.parameters() if p.requires_grad)
    if device == "cuda":
        torch.cuda.reset_peak_memory_stats()
    t0 = time.time()
    result = trainer.train()
    seconds = time.time() - t0
    losses = [h["loss"] for h in trainer.state.log_history if "loss" in h]
    steps = timer.times
    # Seconds per optimizer step, skipping the first 3 steps (warm-up of kernels and caches).
    sps = (steps[-1] - steps[2]) / (len(steps) - 3) if len(steps) > 4 else None
    metrics = {
        "config": dataclasses.asdict(cfg),
        "git_commit": git_commit(),
        "prompt_version": PROMPT_VERSION,
        "prompt_fingerprint": prompt_fingerprint(),
        "items": len(ds),
        "dropped_over_max_length": dropped,
        "ids_sha256": hashlib.sha256("\n".join(ids).encode()).hexdigest(),
        "trainable_params": trainable,
        "steps": result.global_step,
        "seconds": round(seconds, 1),
        "seconds_per_step": None if sps is None else round(sps, 3),
        "examples_per_step": cfg.batch_size * cfg.grad_accum,
        "losses": losses,
        "train_loss": result.training_loss,
        "loss_is_finite": all(l == l and abs(l) != float("inf") for l in losses + [result.training_loss]),
        "peak_gpu_gb": round(torch.cuda.max_memory_allocated() / 1e9, 2) if device == "cuda" else None,
    }
    if cfg.save:
        trainer.save_model(str(out / "final"))
    with open(out / "train_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    return metrics, trainer


def main():
    p = argparse.ArgumentParser()
    for field in dataclasses.fields(RunConfig):
        kind = {"int": int, "float": float, "str": str, "bool": lambda s: s.lower() == "true"}[
            field.type if isinstance(field.type, str) else field.type.__name__]
        p.add_argument("--" + field.name.replace("_", "-"), type=kind,
                       default=None if field.default is dataclasses.MISSING else field.default,
                       required=field.default is dataclasses.MISSING)
    cfg = RunConfig(**vars(p.parse_args()))
    metrics, _ = train(cfg)
    print({k: v for k, v in metrics.items() if k not in ("losses", "dropped_over_max_length")})


if __name__ == "__main__":
    main()
