# finqa-lora

A LoRA fine-tune that teaches a 1.5B model to write FinQA calculation programs, and a hand-checked audit
of FinQA's labels.

- **Model:** [PritRai75/qwen2.5-1.5b-finqa-lora](https://huggingface.co/PritRai75/qwen2.5-1.5b-finqa-lora) on the Hugging Face Hub (LoRA adapter for `Qwen/Qwen2.5-1.5B-Instruct`)
- **Dataset:** [PritRai75/finqa-label-audit](https://huggingface.co/datasets/PritRai75/finqa-label-audit) on the Hugging Face Hub (verdicts and corrections on 198 hand-checked FinQA items)
- **Write-up:** [below](#write-up), after the results

Two linked pieces of work on FinQA (Chen et al., EMNLP 2021), a benchmark of 8,281 expert-written
questions over earnings-report tables and text, each with a gold calculation program.

1. **Label-consistency audit.** A screen of every train, dev and test item for disagreement between the
   gold program's result and the annotator's written answer, followed by a hand-check of samples and of
   every flagged test item.
2. **LoRA fine-tune.** A small open model is trained to write FinQA calculation programs, which Python runs.
   It is compared with the base model, and training on screened data is compared with a random subset of
   the same size.

Test results are below, then the write-up.

## Results (test, 1,147 items)

Every rule that decides a claim below was fixed before the numbers it governs existed; the commits are
named in `handcheck/README.md`, the sections further down and the run reports, and where a rule's text
reached the repo after the work it governs, `handcheck/README.md` says so. Each
percentage is given with its count and a 95% Wilson interval. The test split was scored once, on
20 Nov 2026, at commit `5aa1573` (`results/test/run1/`).

**In short:**
- Fine-tuning `Qwen/Qwen2.5-1.5B-Instruct` with LoRA on about 5,800 FinQA programs takes it from
  1.6% (0-shot) and 5.5% (4-shot) to 63–66% execution accuracy on test. That also beats the larger
  `Qwen/Qwen3-4B-Instruct-2507` prompted with the same 4 examples (22.0%). All 10 fine-tuned runs beat
  each of the three prompted models, in every view.
- Training on the screened data (431 program–answer disagreements removed) against a random subset of
  the same size: **no detectable difference**. Cleaned is ahead by 1.1 points on average and in all 5
  seed pairs, but the interval the rule uses includes zero, so no cleaning effect is claimed.
- The audit: the automatic screen's flags are real label problems 90% of the time on train (45 of 50
  hand-checked) and 92% on test (68 of 74). On test, 86 label problems are confirmed by hand; the
  estimate is 148 and the 95% upper bound 243 of the 1,147 items.

### Execution accuracy

Execution accuracy: the predicted program, run by the official FinQA executor, gives the gold result.
Three views of the same predictions (decision 45, fixed before any test number):

- **official**: all 1,147 items against the shipped `exe_ans`;
- **consistent**: 1,046 items, without every item the hand-check found wrong or could not decide, and
  without the 9 items whose program and answer differ only in sign;
- **corrected**: 1,139 items, with a wrong gold program replaced by Prit's corrected program, and the 2
  ambiguous and 6 undecided items left out.

| Model | official (of 1,147) | consistent (of 1,046) | corrected (of 1,139) |
| --- | --- | --- | --- |
| LoRA, cleaned arm, seeds 1–5 | 745, 762, 750, 754, 759 | 720, 734, 723, 729, 732 | 775, 790, 779, 783, 788 |
| mean | 65.7% | 69.6% | 68.7% |
| LoRA, random arm, seeds 1–5 | 735, 748, 747, 753, 724 | 709, 718, 718, 728, 701 | 761, 773, 774, 779, 754 |
| mean | 64.6% | 68.3% | 67.4% |
| Qwen2.5-1.5B-Instruct, 0-shot | 18 = 1.6% (1.0–2.5%) | 18 = 1.7% (1.1–2.7%) | 18 = 1.6% (1.0–2.5%) |
| Qwen2.5-1.5B-Instruct, 4-shot | 63 = 5.5% (4.3–7.0%) | 62 = 5.9% (4.7–7.5%) | 66 = 5.8% (4.6–7.3%) |
| Qwen3-4B-Instruct-2507, 4-shot | 252 = 22.0% (19.7–24.5%) | 244 = 23.3% (20.9–26.0%) | 260 = 22.8% (20.5–25.4%) |

A single fine-tuned run's interval is about ±2.7 points (cleaned seed 3, the adapter for the Hub:
750 = 65.4%, 62.6–68.1%). Program accuracy (the exact gold program, a stricter measure) for the 10
runs is 676–718 of 1,147. The fine-tuned runs write a program that executes on 1,138–1,145 items;
the prompted 1.5B model on 221 (0-shot) and 435 (4-shot), Qwen3-4B on 972.

**Fine-tuned against prompted** (exact McNemar on the same items; the claim needs all 10 runs to win
at p < 0.05): fine-tuning beats all three prompted models in all three views. Against Qwen3-4B 4-shot,
the closest, each run is right on 528–549 items where Qwen3-4B is wrong, and wrong on 39–56 where it is
right (official view, p ≤ 2.7e-97).

### Cleaned against random

The rule (decision 39) claims "cleaning helped" only if the 95% interval below excludes zero and all 5
seed pairs agree in sign; otherwise "no detectable difference".

| View | Cleaned − random, seed-averaged | 95% interval (the rule's) | Seed pairs 1–5 | Verdict |
| --- | --- | --- | --- | --- |
| official | +1.10 pt | −0.52 to +2.71 | +0.87, +1.22, +0.26, +0.09, +3.05 | no detectable difference |
| consistent | +1.22 pt | −0.39 to +2.83 | +1.05, +1.53, +0.48, +0.10, +2.96 | no detectable difference |
| corrected | +1.30 pt | −0.23 to +2.83 | +1.23, +1.49, +0.44, +0.35, +2.99 | no detectable difference |

The seed pairs all point the same way, but the training noise between seeds (0.84 pt SD on test) is
large enough that a difference of this size is not separable from it with 5 seeds. An interval over
the items alone, reported beside it and deciding nothing, gives +0.19 to +2.01 pt (official) and would
have called a winner: in simulation, before any main run, such intervals declared a winner between
identical arms in 16 to 23% of cases (see "the rule" below). The two-level bootstrap gives
−0.33 to +2.56 pt. Point estimate and interval are the result; a cleaning effect is not.

### The audit

The screen compares each gold program's result with the annotator's written answer. Prit hand-checked
the flags against the report text (`handcheck/`, `results/audit/counts.json`).

| Check | Items | Result |
| --- | --- | --- |
| check1: 50 random train flags | 50 | 45 real label problems: precision 90% (79–96%), about 388 (339–412) of the 431 train flags. Of the 50, a wrong program 31 (62%, 48–74%), a wrong written answer 17 (34%), both in 3; rounding 5; no parser misses |
| check2: every flagged test item | 98 (4 undecided) | 83 of 94 real; on `disagree` items 68 of 74 = 92% (83–96%); all 12 decided empty-answer items are real (11 missing answers). By side: program 38, written answer 25, both 19, question ambiguous 1 |
| check3: 50 random unflagged test items | 50 (2 undecided) | 3 of 48 are real errors the screen missed (6%); one-sided 95% upper bound 15.4%, at most 160 of the 1,040 unflagged items |
| Test set | 1,147 | 86 label problems confirmed; estimate 148; 95% upper bound 243 (the 9 sign-only and 6 undecided items are in no count) |

These are one checker's verdicts. A blind re-check of 20 of them, two days after the first pass
(decision 55), gave the same verdict on 20 of 20 (84–100%; see the write-up below).

Removing the 431 train flags therefore removes about 270 wrong programs (31 of 50, 208–320 of 431)
together with about 120 items whose program is right and only the written answer wrong (14 of 50, 75–180),
which are good training data, and about 40 rounding differences.
This is why the arm is called "removed program–answer disagreements", not "removed wrong programs".

### Error analysis

Every wrong prediction gets one rule-based tag (decision 48, fixed on dev before any test prediction;
`results/errors/test.json`). A fine-tuned run fails 385–423 test items: `other` 150–169, `wrong_number`
88–102, `wrong_table_row` 42–56, `step_count` 23–32, the rest smaller. On the 107 flagged test items
each run fails 69–76, and on 22–26 of those its answer matches the annotator's written answer: the model
agrees with the annotator against the gold program. Qwen3-4B 4-shot's largest failure is a scale slip,
a percentage left as a fraction or the reverse (`scale_x100`, 292 of its 895 failures).

`other` is "none of the rules". Prit hand-tagged 50 of the 266 test items where a fine-tuned run's
failure is tagged `other` (decision 53; drawn by code, seed 20261120; `results/errors/other_tags.json`):

| Hand tag | Items of 50 | Share (95%) |
| --- | --- | --- |
| gold label wrong, or the question ambiguous or unanswerable as scored | 20 | 40% (28–54%) |
| computes another quantity than the question asks (another year, entity or base) | 17 | 34% (22–48%) |
| right quantity, a needed step or term missing | 9 | 18% (10–31%) |
| right quantity, plus unneeded steps | 4 | 8% (3–19%) |
| a number not in the report; a wrong constant; unclear | 0 each | 0% (0–7%) |

These shares describe items with an `other` failure, not all failures. 13 of the 20 gold problems are on
items the screen and the hand-check had not flagged. They were found with a model's prediction in view,
so they are reported here and kept out of the audit counts above.

### Two outputs, as returned

The model replies with a program only; Python runs it. Both are from the Hub adapter (cleaned seed 3),
chosen by position, not by eye: the first test item, and the first test item it gets wrong
(`results/test/run1/cleaned/seed3/test.csv`).

`ETR/2016/page_23.pdf-2`, *what is the net change in net revenue during 2015 for entergy corporation?*

```
subtract(5829, 5735)
```

Runs to 94.0; gold `subtract(5829, 5735)` = 94. Right.

`SYY/2006/page_71.pdf-1`, *what was the percentage change in total rental expense under operating leases
from july 2 , 2005 to july 1 , 2006?*

```
subtract(100690000, 92710000), divide(#0, 92710000)
```

Runs to 0.08607 (8.6%); gold `subtract(92710000, 86842000), divide(#0, 86842000)` = 0.06757, written
answer 7%. Scored wrong; rule tag `wrong_number`. The report gives rental expense of $100,690,000,
$92,710,000 and $86,842,000 "in fiscal 2006, 2005 and 2004" and uses July 1, 2006 and July 2, 2005 as
the fiscal 2006 and 2005 year-ends. On that reading the question asks for fiscal 2005 to 2006, which is
what the model computed, and the gold computes the year before. This reading is Claude's, made after
seeing the prediction; the item is in no hand-check and in no count.

### Training cost

| | |
| --- | --- |
| Base model | `Qwen/Qwen2.5-1.5B-Instruct` at revision `989aa79` |
| Method | LoRA, rank 16, alpha 32, dropout 0.05, on every linear layer of the 28 blocks; 18,464,768 trainable parameters (adapter 73.9 MB in fp32) |
| Training | 5,820 items, 3 epochs, 1,092 steps of 16 examples, learning rate 2e-4, cosine, fp16, length-grouped batches; prompt of `model_input` (the retrieved facts), no truncation |
| Hardware | Kaggle, one NVIDIA T4 (16 GB) per run, two runs in parallel; peak 5.56 GB |
| Time per run | 1.60–1.76 h of training (5.25–5.78 s per step), plus 4.4–4.7 min to score dev |
| All GPU work | 14.8 h of Kaggle session time: feasibility 1.3 h, pilot 3.5 h, the 10 main runs 9.0 h, all 13 test passes 1.0 h |

The trainable-parameter count is computed from the model's configuration (hidden size 1,536, MLP
8,960, 2 key-value heads of 128) and matches the adapter's size; the runs did not log it.

### Checks on the test pass

- Before test was touched, each GPU repeated a committed dev run: 883 of 883 identical replies (cleaned
  seed 1: 588, random seed 1: 583), against a tolerance of 800, fixed beforehand.
- Each adapter was matched to its training run by SHA-256; both base models loaded at pinned Hub
  revisions; the prompt fingerprint `4139bfc3519c` is the one used in training.
- The test gate recorded the commits of the two finished test hand-check sheets.
- Every column of every prediction file was recomputed from the stored reply, and the totals equal the
  run's report. `finqa_lora.testeval` refuses to rebuild `results/test/run1/evaluation.json` if the
  hand-check sheets have changed since the test pass.
- `tests/` pins the committed counts; CI runs them on every push.

## Write-up

**What the project shows.** A 1.5B model fine-tuned with LoRA on about 5,800 FinQA programs reaches
63–66% execution accuracy on test, about three times a 4B model prompted with the same examples, in under
two GPU hours per run. Removing the 431 program–answer disagreements from training made no detectable
difference: the cleaned arm is ahead in all 5 seed pairs, but a rule fixed before the main runs, which
accounts for seed-to-seed noise, keeps zero inside the interval, where an interval over items alone would
have declared a winner. The label audit is the stronger result: on test, 86 label problems are confirmed by
hand (7.5% of the 1,147 items), with an estimate of 148 (12.9%) and a 95% upper bound of 243 (21.2%), and
in a hand-tagged sample of the fine-tuned model's unexplained failures, 40% were label problems rather than
model errors.

**What the screen can and cannot see.** The screen is precise (90% of train flags and 92% of test
`disagree` flags are real), but it only finds items where the gold program and the written answer disagree.
An item where both make the same mistake passes, and so does a written answer off by exactly ×100 or ÷100,
which the screen accepts on purpose. The check3 estimate is there to cover what the screen passes. Both
label problems reported on FinQA's GitHub issues are of this kind, and neither is in a hand-check:
`ANSS/2008/page_89.pdf-1` (issue #15, 2026: a five-year average divided by 4 in both program and answer;
screen `agree`) and `ADI/2009/page_49.pdf-1` (issue #6, 2022: written answer 380 against a program result
of 3.8; screen `agree`). Both are train items, read from the issues and not checked by hand here.

**Retriever setting.** The dev and test facts are FinQA's shipped `model_input`. The pinned data (upstream
commit `0f16e28`, 5 Jun 2022) is upstream's latest. It postdates the fix of a retriever bug that had leaked
label information (4 May 2022; FinQA's README gives the corrected FinQANet RoBERTa-large result as 61.24%
execution accuracy) and the update of the public data with corrected retriever results (`b2eaa71`, 10 May
2022). On 5 Jun 2022 `model_input` was removed and added again with new retrieval fields, and on test its
top 3 facts differ from the 27 May version on 1,066 of 1,147 items. Upstream does not say which retriever
run produced the 5 Jun inputs, so the 61.24% is context here, not a like-for-like comparison.

**Related work.** Northcutt, Athalye and Mueller (NeurIPS 2021, Datasets and Benchmarks) find label errors
in the test sets of 10 common benchmarks, at least 3.3% on average, by flagging candidates automatically and
validating them by hand; about half of their flags were real, against 90–92% for this screen, which is
narrower and only sees one kind of error. Vendrow et al. (2025, "Do Large Language Model Benchmarks Test
Reliability?") show that label errors can hide model failures and propose re-labelled "platinum"
benchmarks; this audit is a partial step of that kind for FinQA, not a corrected test set. The FinQA paper
reports that two experts agreed on 92.65% of 200 sampled items for execution accuracy. A 2025 study of
program-of-thought prompting on FinQA attributes 7% of 100 sampled model errors to ground-truth problems
(arXiv 2510.13157).

**Self-agreement.** 20 hand-checked items (10 `real_error`, 10 others, drawn by code) were checked again
blind two days after the first pass, not the week planned (decision 55): the same verdict on 20 of 20 (95%
Wilson interval 84–100%), Cohen's kappa 1.00 (`results/audit/self_agreement.json`). Outside the definition
fixed beforehand, the error type matched on all 10 real errors and the wrong side on 9; the one change
(`PNC/2012/page_65.pdf-5`, `both` to `program`) turns on the units of the written answer. The short gap makes
remembered verdicts more likely, so 84% is the cautious reading.

**Limits and next steps.** Every verdict is one person's; a second checker on the same 198 items would
measure agreement between people, which the re-check cannot. The random checks are 50 items each, so the
test estimate rests on 3 misses in 48. The 13 error-analysis leads (dataset config
`error_analysis_gold_wrong`) and the two upstream reports are unverified. Re-scoring on a fully corrected
test set, and a cleaning arm that removes only confirmed wrong programs rather than every disagreement,
are the natural next experiments.

## Status

| Part | State |
| --- | --- |
| Data pinned to an upstream commit, checked by SHA-256 | done |
| Official FinQA scorer vendored, parity-tested on all 8,281 gold programs | done |
| Automatic screen (parser v1) | done, counts below |
| Hand-checks: check1 (50 train flags), check2 (all 98 flagged test items), check3 (50 test `agree` items) | done: verdicts committed (check1 `cc61253`, check2 `e467ff5`, check3 `5aa1573`). Parser v1 kept whatever check1 showed |
| Audit counts | done, `results/audit/counts.json` (`finqa_lora/auditcounts.py`, definitions fixed before any verdict); results above |
| Prompt, inference and LoRA training code | done, tested on a tiny model in CI |
| Feasibility run 1 on GPU: licences, token lengths, base models on dev | done, `results/feasibility/run1/` |
| Feasibility run 2: timed LoRA training, cost per run | done, `results/feasibility/run2/` |
| Model choice | `Qwen/Qwen2.5-1.5B-Instruct` for all training (the only candidate under the 2.5 h per-run gate) |
| Pilot: learning rate and epoch on dev, same-seed noise | done, `results/pilot/run1/`; chose learning rate 2e-4, epoch 3 (table below) |
| Main training runs: cleaned versus random, 5 seeds each | done, `results/main/run1/` (seeds 1 to 3) and `results/main/run2/` (seeds 4 and 5); dev table below |
| Test gate: no test inference until check2 and check3 are finished and committed | done (`finqa_lora/testgate.py`) |
| Test passes | done 20 Nov 2026 at `5aa1573`, `results/test/run1/` (Kaggle T4 x2, 59.7 min; `jobs/testpass.sh`); adapters from a private Kaggle dataset, found by SHA-256 |
| Evaluation on test | done, `results/test/run1/evaluation.json` (`finqa_lora/testeval.py`): three views, Wilson intervals, McNemar, the winner rule; results above |
| Error analysis | done: rule-based tags fixed on dev before any test prediction (`finqa_lora/errortags.py`; `results/errors/dev.json`, `test.json`); 50 of the `other` failures tagged by hand (`results/errors/other_tags.json`) |
| Adapter and model card on the Hugging Face Hub | done 22 Nov 2026: [PritRai75/qwen2.5-1.5b-finqa-lora](https://huggingface.co/PritRai75/qwen2.5-1.5b-finqa-lora), cleaned seed 3 (chosen before any test number: median dev score of its arm), public, Apache-2.0. Hub commit `ea894cf` from repo commit `aa50562` (card with the retriever check and the dataset link; first upload `784e802` from `20dd5e2`); all three files downloaded back and matched (`results/hub/upload.json`) |
| Dataset of the hand-checked items, write-up | done 22 Nov 2026: write-up above; dataset [PritRai75/finqa-label-audit](https://huggingface.co/datasets/PritRai75/finqa-label-audit) (decision 57: the 198 hand-checked rows with the 20 second verdicts, and the 13 error-analysis `gold_wrong` leads apart), public, MIT, Hub commit `4c602fa` from repo commit `aa50562`; all three files downloaded back and matched (`results/hub/dataset_upload.json`) |
| Blind re-check of 20 hand-check verdicts | sheet built 22 Nov 2026 (decision 54: 10 `real_error` and 10 others from check1-3, uncertain rows skipped, seed 20261127, `handcheck/recheck.*`); re-checked 22 Nov, two days after the first pass, not the week planned (decision 55): same verdict on 20 of 20 (84–100%), kappa 1.00 (`results/audit/self_agreement.json`) |

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
effect. This changed the cleaned-versus-random rule before any main run reported (see below). Each run took about 1.5 h of training (4.84 to 4.94 s per 16-example step, 5.56 GB peak) plus
about 4 minutes per dev pass.

### Cleaned versus random: the rule, fixed before any main-run result (19 Nov 2026)

"Cleaning helped" (or "hurt") only if the 95% interval on the seed-averaged difference excludes zero
and every seed pair agrees in sign. The interval adds two variances, which items happened to be in
the test set and which training runs happened to come out, and uses a t quantile with
2 × (seeds − 1) degrees of freedom. An interval over items alone ignores the second, and in
simulation (`python -m finqa_lora.rulesim`) it declared a winner between identical arms in 16 to 23%
of cases with 3 seeds once seeds differ by 0.6 to 1.2 accuracy points; this rule stayed at or under
5% in every case. Seeds went from 3 to 5 per arm at the same time: at a seed spread of about 0.6
points, the chance of detecting a real 2-point effect rises from 47% to 78% (simulation).

### Main runs on dev (learning rate 2e-4, epoch 3, 5 seeds per arm; Kaggle T4 x2, 19 Nov 2026)

Dev execution accuracy out of 883 (items whose program executes in brackets). Both arms train on
5,820 items; the random arm is a random subset of train of the same size.

| Seed | Cleaned | Random | Cleaned − random |
| --- | --- | --- | --- |
| 1 | 588 (877) | 583 (880) | +5 |
| 2 | 583 (881) | 582 (881) | +1 |
| 3 | 585 (879) | 588 (880) | −3 |
| 4 | 575 (880) | 589 (879) | −14 |
| 5 | 596 (879) | 584 (878) | +12 |
| Mean (SD) | 585.4 (7.6) = 66.3% | 585.2 (3.1) = 66.3% | +0.2 |

This is not the comparison. Dev chose the learning rate and epoch (on the cleaned arm), and the
cleaned-versus-random decision is made once, on test, with the rule above. What dev does show is the
size of the training noise: the within-arm SD across seeds is 5.8 items, 0.66 accuracy points (8 degrees of
freedom; the 95% range for the true value is about 0.45 to 1.3 points), and two runs with different seeds
give the same reply on 675 to 724 of 883 items (all 45 pairs, either arm), against 833 to 863 for
same-seed repeats in the pilot.
Cleaned seed 1 repeats the pilot's chosen run within the tolerance fixed beforehand (same reply on at
least 800 items, at most 20 right in one run only): 840 and 822 same replies, 11 and 16 right in one only.

Adapters (about 74 MB each) are not committed. Each run's `report.json` records the SHA-256 of its adapter.

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
python -m finqa_lora.auditcounts                  # counts every finished hand-check sheet (results/audit/counts.json)
python -m finqa_lora.runlog build                 # indexes every committed run into runs.db
python -m finqa_lora.testgate                     # is the test split unlocked? (exit 1 while it is not)
python -m finqa_lora.testeval results/test/run1   # views and statistics of a recorded test run
python -m finqa_lora.errortags dev               # one rule-based error tag per wrong dev prediction (results/errors/dev.json)
python -m finqa_lora.errortags test              # the same rules on every pass of results/test/run1 (results/errors/test.json)
python -m finqa_lora.othertags              # builds the hand-tag sheet for the `other` failures (never overwrites one)
python -m finqa_lora.othertags --validate   # checks a filled sheet; --counts counts a finished one (results/errors/other_tags.json)
python -m finqa_lora.recheck                # builds the blind re-check sheet (never overwrites one)
python -m finqa_lora.recheck --validate     # checks a filled sheet; --counts writes results/audit/self_agreement.json
python -m finqa_lora.hfdataset              # builds the dataset files in hub/dataset/ from the committed sheets
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
| `finqa_lora/auditcounts.py` | Counts from the finished hand-check sheets, with intervals; definitions fixed before any verdict |
| `finqa_lora/othertags.py`, `handcheck/tag_other.*` | Hand tags for a random sample of the `other` failures on test (decision 53) |
| `results/screen/` | Screen status for every item |
| `finqa_lora/prompt.py` | The one prompt format used for training, zero-shot and few-shot |
| `finqa_lora/infer.py`, `finqa_lora/train.py` | Greedy generation and scoring; LoRA fine-tuning with TRL |
| `finqa_lora/feasibility.py` | Measures candidate models (dev accuracy, token lengths, training speed) |
| `finqa_lora/pilot.py` | Pilot runs, per-epoch dev scoring, the selection rule and the same-seed noise report |
| `finqa_lora/mainruns.py` | Main runs at the pilot's chosen learning rate and epoch (read from the committed pilot record), adapters kept |
| `finqa_lora/testgate.py` | Keeps the test split locked until the test hand-checks are finished and committed |
| `finqa_lora/testeval.py` | The three test views (official, consistent, corrected) from check2 and check3, and every statistic, from a recorded test run |
| `finqa_lora/testpass.py` | The test passes: 10 adapters (each matched to its committed SHA-256) and 3 prompted base models at pinned Hub revisions, after a dev check that the committed dev replies repeat |
| `finqa_lora/errortags.py`, `results/errors/` | Rule-based error tags for wrong predictions, one per failure, and their dev and test summaries |
| `finqa_lora/stats.py` | Wilson intervals, exact McNemar, item and two-level bootstraps, and the cleaned-versus-random winner rule (variance-components interval plus a sign check over seeds) |
| `finqa_lora/rulesim.py` | Simulation of how often each candidate winner rule declares a winner between identical arms (`results/simulations/winner_rule.json`) |
| `finqa_lora/recheck.py`, `handcheck/recheck.*` | Blind re-check of 20 hand-check verdicts (decision 54): the draw, the sheet, its validator and the self-agreement counts |
| `finqa_lora/hfdataset.py`, `hub/dataset/` | The HF dataset of the hand-checked items (decision 57): files built from the committed sheets, the card, the upload |
| `finqa_lora/hub.py`, `hub/model_card.md` | Upload of the Hub adapter (cleaned seed 3) with its model card: checks the adapter's SHA-256, uploads the committed card and config, downloads all three back and compares hashes (`results/hub/upload.json`) |
| `finqa_lora/runlog.py` | Builds `runs.db` (not committed) from `results/`: one row per run with its commit, config, prompt and adapter hashes, one row per item |
| `finqa_lora/tiny.py` | Tiny random-weight model for CPU tests |
| `notebooks/kaggle_job.ipynb`, `scripts/kaggle_run.sh`, `jobs/` | Kaggle launcher, runner script and one file per GPU job |
| `results/feasibility/` | Reports, logs and dev predictions of the feasibility runs |
| `results/pilot/`, `results/main/` | Reports, logs, training states and dev predictions of the pilot and main runs (adapters not committed) |

## Data and licence

FinQA is MIT licensed (Copyright (c) 2021 Zhiyu Chen), from https://github.com/czyssrs/FinQA. This repo is MIT licensed.
