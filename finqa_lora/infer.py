"""Greedy generation of programs, then scoring with the official FinQA code.

Usage (GPU):
  python -m finqa_lora.infer --model Qwen/Qwen2.5-1.5B-Instruct --split dev --shots 0 --out results/x.csv
  python -m finqa_lora.infer --model <base> --adapter <dir> --split dev --out results/y.csv
"""
import argparse
import csv
import time

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from finqa_lora.data import load_split
from finqa_lora.prompt import extract_program, few_shot_examples, messages
from finqa_lora.scoring import exe_correct, execute, prog_correct

MAX_NEW_TOKENS = 96  # longest gold program is 122 characters, well under 96 tokens


def device_and_dtype():
    # T4 has no fast bfloat16, so fp16 on GPU; fp32 on CPU for tests.
    return ("cuda", torch.float16) if torch.cuda.is_available() else ("cpu", torch.float32)


def load_tokenizer(model_id):
    tok = AutoTokenizer.from_pretrained(model_id)
    tok.padding_side = "left"
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    return tok


def load_model(model_id, adapter=None):
    device, dtype = device_and_dtype()
    model = AutoModelForCausalLM.from_pretrained(model_id, dtype=dtype).to(device)
    if adapter:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, adapter)
    model.eval()
    return model


def prompts_for(tok, examples, shots):
    return [tok.apply_chat_template(messages(ex, shots), tokenize=False, add_generation_prompt=True)
            for ex in examples]


@torch.no_grad()
def generate(model, tok, prompts, batch_size=16, max_new_tokens=MAX_NEW_TOKENS):
    """Return one decoded reply per prompt, in input order. Batches are length-sorted."""
    order = sorted(range(len(prompts)), key=lambda i: len(prompts[i]))
    out = [None] * len(prompts)
    device = next(model.parameters()).device
    for start in range(0, len(order), batch_size):
        idx = order[start:start + batch_size]
        enc = tok([prompts[i] for i in idx], return_tensors="pt", padding=True,
                  add_special_tokens=False).to(device)
        gen = model.generate(**enc, max_new_tokens=max_new_tokens, do_sample=False,
                             pad_token_id=tok.pad_token_id)
        new = gen[:, enc["input_ids"].shape[1]:]
        for i, text in zip(idx, tok.batch_decode(new, skip_special_tokens=True)):
            out[i] = text
    return out


def score_rows(examples, replies):
    rows = []
    for ex, reply in zip(examples, replies):
        program = extract_program(reply)
        ok, value = execute(program, ex["table"]) if program else (False, None)
        rows.append({
            "id": ex["id"],
            "reply": reply.strip(),
            "program": program,
            "executes": int(ok),
            "value": "" if value is None else value,
            "exe_correct": int(bool(program) and exe_correct(program, ex)),
            "prog_correct": int(bool(program) and prog_correct(program, ex)),
        })
    return rows


def write_rows(rows, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def summarize(rows):
    n = len(rows)
    return {
        "items": n,
        "exe_correct": sum(r["exe_correct"] for r in rows),
        "prog_correct": sum(r["prog_correct"] for r in rows),
        "executes": sum(r["executes"] for r in rows),
        "exe_acc": sum(r["exe_correct"] for r in rows) / n,
    }


def run(model_id, split, shots=0, adapter=None, limit=None, batch_size=16, model=None, tok=None):
    """Generate and score. Returns (rows, summary dict with timing)."""
    tok = tok or load_tokenizer(model_id)
    model = model or load_model(model_id, adapter)
    examples = load_split(split)[:limit]
    shot_examples = few_shot_examples(load_split("train"))[:shots] if shots else ()
    prompts = prompts_for(tok, examples, shot_examples)
    t0 = time.time()
    replies = generate(model, tok, prompts, batch_size=batch_size)
    seconds = time.time() - t0
    rows = score_rows(examples, replies)
    summary = summarize(rows) | {"split": split, "shots": shots, "seconds": round(seconds, 1),
                                 "prompt_tokens_mean": round(sum(len(tok(p, add_special_tokens=False)["input_ids"])
                                                                 for p in prompts) / len(prompts), 1)}
    return rows, summary


def main():
    from pathlib import Path
    p = argparse.ArgumentParser()
    p.add_argument("--model", required=True)
    p.add_argument("--adapter")
    p.add_argument("--split", default="dev", choices=["dev", "test"])
    p.add_argument("--shots", type=int, default=0)
    p.add_argument("--limit", type=int)
    p.add_argument("--batch-size", type=int, default=16)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    rows, summary = run(a.model, a.split, a.shots, a.adapter, a.limit, a.batch_size)
    write_rows(rows, Path(a.out))
    print(summary)


if __name__ == "__main__":
    main()
