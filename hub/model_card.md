---
base_model: Qwen/Qwen2.5-1.5B-Instruct
library_name: peft
license: apache-2.0
language:
- en
pipeline_tag: text-generation
tags:
- lora
- peft
- finqa
- financial-qa
- numerical-reasoning
- program-generation
---

# Qwen2.5-1.5B-Instruct + LoRA for FinQA programs

A LoRA adapter for `Qwen/Qwen2.5-1.5B-Instruct` that reads facts from a company's financial report
and a question, and writes a FinQA calculation program such as `subtract(5829, 5735), divide(#0, 5735)`.
The model writes the program; Python runs it. It was trained and evaluated in
[PritRai75/finqa-lora](https://github.com/PritRai75/finqa-lora), which holds the code, every run's
record and a label audit of FinQA. This card is `hub/model_card.md` in that repo.

On the FinQA test set (1,147 questions) this adapter gets **750 right = 65.4% (95% interval 62.6–68.1%)**
execution accuracy, against 1.6% for the same base model prompted with no examples and 22.0% for
`Qwen/Qwen3-4B-Instruct-2507` prompted with 4 examples.

## Results on test

Execution accuracy: the predicted program, run by the official FinQA executor, gives the gold result.
Greedy decoding, no examples in the prompt. The test split was scored once, on 20 Nov 2026, at repo
commit `5aa1573`. Intervals are 95% Wilson intervals.

| View | Items | This adapter |
| --- | --- | --- |
| official | 1,147 | 750 = 65.4% (62.6–68.1%) |
| consistent | 1,046 | 723 = 69.1% (66.3–71.8%) |
| corrected | 1,139 | 779 = 68.4% (65.6–71.0%) |

- **official**: every test item, scored against FinQA's shipped answer.
- **consistent**: without the items whose label a hand-check found wrong or could not decide, and the
  9 items whose program and written answer differ only in sign.
- **corrected**: a wrong gold program replaced by a hand-corrected one; 2 ambiguous and 6 undecided
  items left out.

The program executes on 1,143 of 1,147 items; it is the exact gold program on 708 (program accuracy).

For comparison, official view, same prompt and scorer:

| Model | Test, official |
| --- | --- |
| `Qwen/Qwen2.5-1.5B-Instruct`, 0-shot | 18 = 1.6% |
| `Qwen/Qwen2.5-1.5B-Instruct`, 4-shot | 63 = 5.5% |
| `Qwen/Qwen3-4B-Instruct-2507`, 4-shot | 252 = 22.0% |
| 10 LoRA runs (2 data arms × 5 seeds), this one included | 63.1–66.4% |

Against Qwen3-4B 4-shot, this adapter is right on 539 items where Qwen3-4B is wrong and wrong on 41
where it is right (exact McNemar p = 7.7e-112).

### Why this run

It was fixed before any test number existed: the run from the "cleaned" arm with the median dev score
of its five seeds (seed 3, 585 of 883 on dev; the arm scored 575, 583, 585, 588, 596). It is not the
best run on test: of its arm's five runs it is the second lowest (745, 750, 754, 759, 762).

### What "cleaned" means, and what it did not show

The cleaned arm trains on FinQA train minus the 431 items where an automatic screen found the gold
program's result disagreeing with the annotator's written answer (5,820 of 6,251 items). A second arm
trained on a random subset of the same size. On test, cleaned is ahead by +1.10 points (seed-averaged,
official view), but the interval of the rule fixed before any main-run result is −0.52 to +2.71, which
includes zero: **no detectable difference**. This adapter is not evidence that removing those items helps.

## How to use

The prompt must be exactly the one used in training (prompt version 1, fingerprint `4139bfc3519c`).
The model does not retrieve: you give it the relevant facts, one per line, as FinQA's `model_input`
does (sentences, and table rows written as sentences).

```python
SYSTEM = (
    "You answer questions about a company's financial report by writing a program that a calculator runs.\n"
    "Operations with two arguments: add, subtract, multiply, divide, exp, greater.\n"
    "Operations over a table row: table_sum, table_average, table_max, table_min, written as "
    "table_average(row name, none).\n"
    "An argument is a number copied from the facts, a constant such as const_100 or const_1000, "
    "or #n for the result of step n, counting from 0.\n"
    "Reply with the program only, on one line, for example: subtract(5829, 5735), divide(#0, 5735)"
)


def build_messages(facts, question):
    facts_text = "\n".join(f"- {fact}" for fact in facts)
    return [{"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"Facts:\n{facts_text}\n\nQuestion: {question}"}]
```

```python
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

BASE = "Qwen/Qwen2.5-1.5B-Instruct"
REVISION = "989aa7980e4cf806f80c7fef2b1adb7bc71aa306"   # the base revision used at test

tok = AutoTokenizer.from_pretrained(BASE, revision=REVISION)
model = AutoModelForCausalLM.from_pretrained(BASE, revision=REVISION, dtype=torch.float16).to("cuda")
model = PeftModel.from_pretrained(model, "PritRai75/qwen2.5-1.5b-finqa-lora").eval()

facts = [
    "the 2014 net revenue of amount ( in millions ) is $ 5735 ;",
    "the volume/weather of amount ( in millions ) is 95 ;",
    "the 2015 net revenue of amount ( in millions ) is $ 5829 ;",
]
question = "what is the net change in net revenue during 2015 for entergy corporation?"
prompt = tok.apply_chat_template(build_messages(facts, question), tokenize=False, add_generation_prompt=True)
enc = tok(prompt, return_tensors="pt", add_special_tokens=False).to(model.device)
out = model.generate(**enc, max_new_tokens=96, do_sample=False)
print(tok.decode(out[0, enc["input_ids"].shape[1]:], skip_special_tokens=True))
# subtract(5829, 5735)
```

The example is the first FinQA test item (`ETR/2016/page_23.pdf-2`); the reply shown is the one this
adapter gave in the test pass. To run a program, use the official FinQA executor (`eval_program` in
FinQA's `evaluate.py`). To repeat the evaluation itself (same prompt code, batching, program
extraction and scorer), use the repo:

```bash
git clone https://github.com/PritRai75/finqa-lora && cd finqa-lora
pip install -r requirements.txt -r requirements-gpu.txt   # on top of a CUDA build of torch
python -m finqa_lora.fetch                                 # FinQA at the pinned upstream commit
python -m finqa_lora.infer --model Qwen/Qwen2.5-1.5B-Instruct \
    --adapter PritRai75/qwen2.5-1.5b-finqa-lora --split dev --out dev.csv
```

`infer` loads the base model's current `main`. On a Kaggle T4 in fp16, the training run's own dev
scoring gave 585 of 883. The evaluation used left-padded batches of 16;
GPU generation is not bit-reproducible, so another GPU, batch size or dtype can change a few replies.

## Training

| | |
| --- | --- |
| Base model | `Qwen/Qwen2.5-1.5B-Instruct` |
| Data | FinQA train at upstream commit `0f16e28`, cleaned arm: 5,820 items (ids SHA-256 `3eeb7b6b…47b1a5`) |
| Input | system prompt above; user turn = FinQA's `model_input` facts and the question; target = the gold program; loss on the program only |
| LoRA | rank 16, alpha 32, dropout 0.05, on q, k, v, o, gate, up and down projections of all 28 blocks; 18,464,768 trainable parameters |
| Schedule | 3 epochs, 1,092 steps of 16 examples (8 × 2 accumulation), learning rate 2e-4, cosine, 3% warm-up, fp16, length-grouped batches, max length 1,024 tokens, nothing truncated or dropped |
| Choice of settings | learning rate and epoch chosen on dev in a pilot, before the main runs |
| Hardware and time | one NVIDIA T4 on Kaggle; 1.66 h of training (5.464 s per step), peak 5.56 GB |
| Final training loss | 0.0750 |
| Software | torch 2.11.0+cu130, transformers 5.22.2, peft 0.21.2, trl 1.17.1 |
| Code | repo commit `0d172f7`, `finqa_lora/train.py` |

Training loaded the base model's Hub `main` without a pinned revision. `main` was
`989aa7980e4cf806f80c7fef2b1adb7bc71aa306` when recorded before training (10 Nov 2026) and at the test
pass (20 Nov 2026); the test pass loaded that revision explicitly.

## Limitations

- **Retriever setting.** Dev and test facts are FinQA's shipped `model_input`, the top 3 from the
  paper's retriever. Whether the shipped test inputs predate or follow FinQA's later retriever fix has
  not been checked, so these numbers are not placed beside published FinQA scores.
- **Label errors in the test set.** A hand-check of the test set confirmed 86 label problems among the
  1,147 items (estimate 148, 95% upper bound 243). The official score therefore marks some right
  programs wrong and some wrong ones right; the consistent and corrected views are the check on that.
  The hand-checks are one checker's verdicts.
- **Where it fails.** It gets 397 test items wrong. By rule-based tag: 158 none of the rules
  (`other`), 102 a wrong number, 47 a wrong table row, 25 operands in the wrong order, 24 a wrong
  number of steps, 20 a wrong operation, 13 a percentage scaled by 100 or not, 4 a sign, 4 an invalid
  program. In a hand-tagged sample of `other` failures across the 10 runs, the commonest cause after
  label problems was computing a different quantity than asked (another year, entity or base).
- **Scope.** Trained and tested only on FinQA: English questions over earnings reports of S&P 500
  companies. Training examples were at most 852 tokens (prompt and program); longer inputs were never
  seen. It has not been tested on other documents, on facts it has to find itself, or on questions that
  are not calculations.
- **Not for decisions.** It writes a program; check the program and the numbers it copies before
  relying on the result. It is not financial advice.

## Files

| File | Bytes | SHA-256 |
| --- | --- | --- |
| `adapter_model.safetensors` | 73,911,112 | `21f55ad225b8ff60e292d31c5ee85a0a3d7ea12af5c0c3c7a899c74ef774a107` |
| `adapter_config.json` | 1,182 | `e504a787317b091bceaeccc78bb767adfa1c6af6b3c278e96586958f60a838bf` |

The adapter's SHA-256 is the one recorded by its training run (`results/main/run1/report.json` in the
repo) and checked again by the test pass before it scored test.

## Licence and data

The adapter is released under Apache-2.0, the base model's licence. FinQA is MIT licensed
(Copyright (c) 2021 Zhiyu Chen), from https://github.com/czyssrs/FinQA. The repo's code is MIT licensed.

```bibtex
@inproceedings{chen-etal-2021-finqa,
    title = "{F}in{QA}: A Dataset of Numerical Reasoning over Financial Data",
    author = "Chen, Zhiyu and Chen, Wenhu and Smiley, Charese and Shah, Sameena and Borova, Iana and
      Langdon, Dylan and Moussa, Reema and Beane, Matt and Huang, Ting-Hao and Routledge, Bryan and
      Wang, William Yang",
    booktitle = "Proceedings of the 2021 Conference on Empirical Methods in Natural Language Processing",
    year = "2021",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2021.emnlp-main.300/",
    doi = "10.18653/v1/2021.emnlp-main.300",
    pages = "3697--3711"
}
```
