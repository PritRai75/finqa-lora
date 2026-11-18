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
| Hand-check 1 (50 train flags) | sheet built, verdicts in progress |
| Prompt, inference and LoRA training code | done, tested on a tiny model in CI |
| Feasibility run 1 on GPU: licences, token lengths, base models on dev | done, `results/feasibility/run1/` |
| Feasibility run 2: timed LoRA training, cost per run | done, `results/feasibility/run2/` |
| Model choice | `Qwen/Qwen2.5-1.5B-Instruct` for all training (the only candidate under the 2.5 h per-run gate) |
| Pilot: learning rate and epoch on dev, same-seed noise | done, `results/pilot/run1/`; chose learning rate 2e-4, epoch 3 (table below) |
| Main training runs: cleaned versus random, 3 seeds each | ready (`jobs/main.sh`), configuration frozen from the pilot |
| Test gate: no test inference until check2 and check3 are finished and committed | done (`finqa_lora/testgate.py`) |
| Test passes and evaluation | not started |

### Screen counts (automatic, not hand-checked)

| Split | Items | agree | disagree | sign only | unparsed | no answer |
| --- | --- | --- | --- | --- | --- | --- |
| train | 6,251 | 5,656 | 431 | 63 | 53 | 48 |
| dev | 883 | 803 | 57 | 8 | 3 | 12 |
| test | 1,147 | 1,040 | 76 | 9 | 8 | 14 |

A `disagree` is a flag, not a confirmed error. The hand-check decides which flags are real and which side is wrong.

### Pilot (dev, cleaned arm, seed 1; Kaggle T4 x2, 16 Nov 2026)

Dev execution accuracy out of 883, each setting trained twice with the same seed (runs a and b).
Selection rule fixed before the run: highest mean of a and b; ties to fewer epochs, then the lower learning rate.

| Learning rate | Epoch 1 (a / b) | Epoch 2 (a / b) | Epoch 3 (a / b) |
| --- | --- | --- | --- |
| 1e-4 | 574 / 566 | 576 / 574 | 576 / 579 |
| 2e-4 | 566 / 565 | 581 / 582 | **589 / 582** (chosen) |

For scale, the base 1.5B model scores 29 (zero-shot) and 43 (4-shot) on the same items, and Qwen3-4B 224
and 221 (`results/feasibility/run1/`). Dev was used to choose the setting, so these dev numbers are not
the result; the test passes are.

GPU training with the same seed and the same batches is not bit-reproducible: adapters differed in all 6
pairs, and replies differed on 20 to 50 of 883 items. Two of the six pairs differ at exact McNemar
p = 0.039, so a per-item test between two training runs cannot by itself separate training noise from an
effect. Each run took about 1.5 h of training (4.84 to 4.94 s per 16-example step, 5.56 GB peak) plus
about 4 minutes per dev pass.

## Run it

Python 3.13 (CI uses the same).

```bash
python -m venv .venv && source .venv/Scripts/activate   # Git Bash on Windows; use .venv/bin/activate elsewhere
pip install -r requirements.txt
python -m finqa_lora.fetch       # downloads train/dev/test at the pinned commit (about 103 MB)
pytest                           # manifest, scorer parity, screen counts
python -m finqa_lora.screen      # writes results/screen/
python -m finqa_lora.handcheck check1             # builds the sheet (never overwrites one)
python -m finqa_lora.handcheck check1 --validate  # lists invalid or changed values in a filled sheet
python -m finqa_lora.runlog build                 # indexes every committed run into runs.db
python -m finqa_lora.testgate                     # is the test split unlocked? (exit 1 while it is not)
```

Fill hand-check sheets in a text editor, not Excel: a spreadsheet save rewrites the item columns
(`43.9%` to `43.90%`, `0.0` to `0`), and `--validate` then refuses the sheet.

GPU jobs run on Kaggle through `notebooks/kaggle_job.ipynb`. It clones this repo at a given commit and
runs `scripts/kaggle_run.sh <job>`, which installs `requirements-gpu.txt` on top of Kaggle's torch, downloads
the pinned data and runs `jobs/<job>.sh`, stopping at the first error. Each job file records exactly what
ran. The test split is not used until the final runs: `finqa_lora.infer` refuses to generate on it until
check2 and check3 have a verdict on every row, pass `--validate` and are committed (`finqa_lora/testgate.py`),
and each test pass records which commit of those sheets let it through.

## Layout

| Path | What it holds |
| --- | --- |
| `data/manifest.json` | Upstream commit, sizes and SHA-256 of the data and the vendored scorer |
| `third_party/finqa_official/` | Unmodified official `evaluate.py` and its MIT licence |
| `finqa_lora/scoring.py` | Execution and program accuracy through the official code |
| `finqa_lora/screen.py` | The automatic program-versus-answer screen |
| `finqa_lora/handcheck.py`, `handcheck/` | Hand-check sheets and protocol |
| `results/screen/` | Screen status for every item |
| `finqa_lora/prompt.py` | The one prompt format used for training, zero-shot and few-shot |
| `finqa_lora/infer.py`, `finqa_lora/train.py` | Greedy generation and scoring; LoRA fine-tuning with TRL |
| `finqa_lora/feasibility.py` | Measures candidate models (dev accuracy, token lengths, training speed) |
| `finqa_lora/pilot.py` | Pilot runs, per-epoch dev scoring, the selection rule and the same-seed noise report |
| `finqa_lora/mainruns.py` | Main runs at the pilot's chosen learning rate and epoch (read from the committed pilot record), adapters kept |
| `finqa_lora/testgate.py` | Keeps the test split locked until the test hand-checks are finished and committed |
| `finqa_lora/stats.py` | Wilson intervals, exact McNemar, paired bootstrap and the cleaned-versus-random winner rule |
| `finqa_lora/runlog.py` | Builds `runs.db` (not committed) from `results/`: one row per run with its commit, config, prompt and adapter hashes, one row per item |
| `finqa_lora/tiny.py` | Tiny random-weight model for CPU tests |
| `notebooks/kaggle_job.ipynb`, `scripts/kaggle_run.sh`, `jobs/` | Kaggle launcher, runner script and one file per GPU job |
| `results/feasibility/` | Reports, logs and dev predictions of the feasibility runs |

## Data and licence

FinQA is MIT licensed (Copyright (c) 2021 Zhiyu Chen), from https://github.com/czyssrs/FinQA. This repo is MIT licensed.
