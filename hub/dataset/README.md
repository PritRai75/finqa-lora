---
license: mit
language:
- en
pretty_name: FinQA label audit (hand-checked items)
size_categories:
- n<1K
task_categories:
- question-answering
- table-question-answering
tags:
- finqa
- label-noise
- data-quality
- financial-qa
- numerical-reasoning
configs:
- config_name: hand_checks
  data_files: hand_checks.csv
  default: true
- config_name: error_analysis_gold_wrong
  data_files: error_analysis_gold_wrong.csv
---

# FinQA label audit: hand-checked items

Hand-checked verdicts on 198 items of [FinQA](https://github.com/czyssrs/FinQA) (Chen et al., EMNLP 2021),
a benchmark of questions over earnings reports in which every item has a gold calculation program and an
annotator's written answer. Each verdict says whether the item's label is wrong, which side is wrong (the
program, the written answer, both, or the question), what kind of error it is, and the corrected answer and
program. The audit, its code and its rules are in [PritRai75/finqa-lora](https://github.com/PritRai75/finqa-lora);
this card is `hub/dataset/README.md` there. A model fine-tuned in the same project is
[PritRai75/qwen2.5-1.5b-finqa-lora](https://huggingface.co/PritRai75/qwen2.5-1.5b-finqa-lora).

Headline: on the FinQA test set (1,147 items), **86 label problems are confirmed by hand**; scaling the
miss rate of a random check of the unflagged items gives an estimate of 148 and a 95% upper bound of 243.

## What is in it

| Config | Rows | What |
| --- | --- | --- |
| `hand_checks` (default) | 198 | Every item of the three hand-checks below, with its first verdict; 20 of them also carry a blind second verdict |
| `error_analysis_gold_wrong` | 13 | Test items found to have a wrong label during error analysis of a model's mistakes; not part of the audit (see below) |

```python
from datasets import load_dataset

checks = load_dataset("PritRai75/finqa-label-audit", "hand_checks", split="train")
extra = load_dataset("PritRai75/finqa-label-audit", "error_analysis_gold_wrong", split="train")
```

The `id` column is FinQA's own id, so each row joins to the full item (report text, table, `model_input`)
in FinQA's `train.json` or `test.json`; the repo pins FinQA at upstream commit `0f16e28`.

## How the items were chosen

An automatic screen compared each gold program's result with the written answer and gave every item a
status: `agree`, `disagree` (a flag), `sign_only`, `unparsed` or `no_answer`. Three checks were then done
by hand:

| `check` | Items | Chosen how | Measures |
| --- | --- | --- | --- |
| `check1` | 50 train items | at random (seed 20261103) from the 431 train `disagree` flags | how many flags are real label problems (the screen's precision) |
| `check2` | 98 test items | every test item that is `disagree`, `unparsed` or `no_answer` (a census) | the confirmed test-set problems |
| `check3` | 50 test items | at random (seed 20261103) from the 1,040 test `agree` items | how many problems the screen misses |

The sample is therefore **not** a random sample of FinQA: flagged items are heavily over-represented.
Use `check1` and `check3` for rates; `check2` is exact for the flagged part of the test set.

## Results

| Check | Result |
| --- | --- |
| check1 | 45 of 50 flags are real label problems: 90% (79–96%). Of the 50, a wrong program 31, a wrong written answer 17 |
| check2 | 83 of 94 decided items are real problems (4 undecided); on `disagree` items 68 of 74 = 92% (83–96%); 11 missing answers |
| check3 | 3 of 48 decided items are real problems the screen missed; one-sided 95% upper bound 15.4% |
| Test set | 86 confirmed; estimate 148; 95% upper bound 243 of 1,147 |

Intervals are 95% Wilson intervals. Counts are from `results/audit/counts.json` in the repo; their
definitions were fixed before any verdict.

## Columns of `hand_checks`

| Column | Meaning |
| --- | --- |
| `check`, `item` | Which check, and the row number in that check's sheet |
| `id`, `split` | FinQA's id and split (`train` or `test`) |
| `screen_status` | The automatic screen's status (shown to the checker) |
| `question`, `written_answer`, `exe_ans`, `gold_program` | As in FinQA: the question, the annotator's answer, the gold program's result and the gold program |
| `verdict` | `real_error` (the program, the written answer or the question is wrong), `no_error`, `parser_miss` (the screen misread a right answer), `rounding` (the answer is the right value rounded), `sign_convention` (the same change with opposite signs) |
| `wrong_side` | For `real_error`: `program`, `answer`, `both` or `question_ambiguous` |
| `error_type` | For `real_error`: the first thing to fix on the wrong side: `wrong_number`, `wrong_table_row`, `wrong_operation`, `operand_order`, `step_count`, `scale_or_units`, `answer_typo`, `missing_answer`, `other` |
| `corrected_answer`, `corrected_program` | The right answer; the right program (FinQA syntax) when the program is wrong |
| `uncertain` | `true` when the checker could not decide; such rows are in no count |
| `note` | The checker's one-line reason, with the numbers |
| `recheck_verdict`, `recheck_uncertain`, `recheck_note` | The blind second verdict, for the 20 re-checked items; empty otherwise |

FinQA conventions are not counted as errors: a percentage written as a fraction in the program, amounts
in the report's units, a decline answered as a positive size. The full rules, boundary cases and the
decisions behind them are in `handcheck/README.md` in the repo.

## Self-agreement

20 of the items (10 first-pass `real_error`, 10 others, uncertain rows skipped, drawn by code with seed
20261127) were checked again blind on 22 Nov 2026, two days after the first pass, not the week planned
(decision 55), with no first verdict in view. The same verdict came back on **20 of 20** (95% Wilson
interval 84–100%), Cohen's kappa 1.00, both on the five verdicts and on `real_error` versus not. Outside
that definition, which was fixed before the re-check: on the 10 real errors the error type matched on all 10
and the wrong side on 9; the one change (`PNC/2012/page_65.pdf-5`) moved from `both` to `program` on whether
the written answer 275.124 is read in the question's millions. A two-day gap makes remembered verdicts more
likely, which would raise the agreement, so the lower end of the interval, 84%, is the cautious reading. The
second verdicts are in `recheck_verdict`, `recheck_uncertain` and `recheck_note`; counts in
`results/audit/self_agreement.json` in the repo.

## The `error_analysis_gold_wrong` config

While analysing a fine-tuned model's mistakes on test, 50 items whose failure fit no rule-based tag were
tagged by hand. 20 of them were tagged `gold_wrong`: the label is wrong, or the question is ambiguous or
unanswerable as scored. 7 of those were already confirmed in `check2`; the other **13** were on `agree`
items that no hand-check covered, and they are this config. They differ from `hand_checks` in three ways:
the checker saw a model's prediction (`pred_program`, `pred_value`, from `shown_pass`) while judging; there
is no corrected answer or program, only the `note`; and they are in **no** count above. Treat them as leads,
not as a measured rate.

## Limitations

- **One checker.** Every verdict is the repo author's. The re-check measures how stable one person's
  verdicts are, not agreement between people.
- **Judged from what FinQA provides.** Each item was read with the report page FinQA ships (text before
  and after the table, and the table), not the full filing.
- **Small random checks.** `check1` and `check3` are 50 items each, so rates have wide intervals; the test
  estimate of 148 rests on 3 misses in 48.
- **Not a corrected FinQA.** Only these 198 items are checked. Items outside them, and the 13 leads, are
  not verified.

## Licence and citation

MIT, as FinQA (Copyright (c) 2021 Zhiyu Chen; the questions, answers and programs here are FinQA's). The
verdicts, corrections and notes are the repo author's.

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
