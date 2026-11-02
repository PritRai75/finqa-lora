# finqa-lora

Work in progress. Two linked pieces of work on FinQA (Chen et al., EMNLP 2021), a benchmark of
8,281 expert-written questions over earnings-report tables and text, each with a gold calculation program.

1. **Label-consistency audit.** A screen of every train, dev and test item for disagreement between the
   gold program's result and the annotator's written answer, followed by a hand-check of samples and of
   every flagged test item.
2. **LoRA fine-tune.** A small open model is trained to write FinQA calculation programs, which Python runs.
   It is compared with the base model, and training on screened data is compared with a random subset of
   the same size.

No results yet. Numbers will be added here only from completed runs.

## Status

| Part | State |
| --- | --- |
| Data pinned to an upstream commit, checked by SHA-256 | done |
| Official FinQA scorer vendored, parity-tested on all 8,281 gold programs | done |
| Automatic screen (parser v1) | done, counts below |
| Hand-check 1 (50 train flags) | not started |
| Training and evaluation | not started |

### Screen counts (automatic, not hand-checked)

| Split | Items | agree | disagree | sign only | unparsed | no answer |
| --- | --- | --- | --- | --- | --- | --- |
| train | 6,251 | 5,656 | 431 | 63 | 53 | 48 |
| dev | 883 | 803 | 57 | 8 | 3 | 12 |
| test | 1,147 | 1,040 | 76 | 9 | 8 | 14 |

A `disagree` is a flag, not a confirmed error. The hand-check decides which flags are real and which side is wrong.

## Run it

Python 3.13 (CI uses the same).

```bash
python -m venv .venv && source .venv/Scripts/activate   # Git Bash on Windows; use .venv/bin/activate elsewhere
pip install -r requirements.txt
python -m finqa_lora.fetch       # downloads train/dev/test at the pinned commit (about 103 MB)
pytest                           # manifest, scorer parity, screen counts
python -m finqa_lora.screen      # writes results/screen/
python -m finqa_lora.handcheck check1
```

## Layout

| Path | What it holds |
| --- | --- |
| `data/manifest.json` | Upstream commit, sizes and SHA-256 of the data and the vendored scorer |
| `third_party/finqa_official/` | Unmodified official `evaluate.py` and its MIT licence |
| `finqa_lora/scoring.py` | Execution and program accuracy through the official code |
| `finqa_lora/screen.py` | The automatic program-versus-answer screen |
| `finqa_lora/handcheck.py`, `handcheck/` | Hand-check sheets and protocol |
| `results/screen/` | Screen status for every item |

## Data and licence

FinQA is MIT licensed (Copyright (c) 2021 Zhiyu Chen), from https://github.com/czyssrs/FinQA. This repo is MIT licensed.
