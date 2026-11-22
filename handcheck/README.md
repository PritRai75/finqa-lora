# Hand-check protocol

Every verdict in this folder is made by hand by the repo author. Code only builds the sheets
(`python -m finqa_lora.handcheck check1`), checks filled sheets (`--validate`) and later counts
the filled columns. The rules below were fixed on 10 Nov 2026, before check1 started; decisions 49–52
were added on 20 Nov 2026, during check2, before any count.

## The three checks

| Check | Items | What it measures |
| --- | --- | --- |
| check1 | 50 random train items the screen flagged (`disagree`) | Precision of the screen, and how many flags are a wrong program rather than a wrong written answer |
| check2 | Every test item that is `disagree`, `unparsed` or `no_answer` | Confirmed test-set errors, by wrong side |
| check3 | 50 random test items the screen passed (`agree`) | An upper bound on the errors the screen misses |

Read each item in `<check>.md` and record the verdict in the matching row of `<check>.csv`.
Work out the right answer from the question and the report first, then judge the gold program
and the written answer against it, each on its own.

## Columns to fill

| Column | Values |
| --- | --- |
| `verdict` | `real_error`, `no_error`, `parser_miss`, `rounding`, `sign_convention` |
| `wrong_side` | Only for `real_error`: `program`, `answer`, `both`, `question_ambiguous` |
| `error_type` | Only for `real_error`, empty for `question_ambiguous`: `wrong_number`, `wrong_table_row`, `wrong_operation`, `operand_order`, `step_count`, `scale_or_units`, `answer_typo` (answer only), `missing_answer` (answer only), `other` |
| `corrected_answer` | The right answer, for every `real_error` except `question_ambiguous` |
| `corrected_program` | The right program in FinQA syntax, when `wrong_side` is `program` or `both` |
| `uncertain` | `true` if you cannot decide. The item is then left out of every count |
| `note` | One line: what is wrong and the right calculation with its numbers |

## Meaning of each verdict

- `real_error`: the program, the written answer or the question is wrong.
- `no_error`: both are right (mainly check3).
- `parser_miss`: the screen misread the written answer (a units word, a range, free text) and it means the right value.
- `rounding`: the written answer is the right value rounded more coarsely than the screen allowed, the report gives the same figure at two precisions, or the gap is under 1% of the right value and no specific calculation explains it. A digit slip is such an explanation: two adjacent digits swapped, or one digit other than the last changed, is `real_error` / `answer` / `answer_typo` even under 1%; a gap in the last digit alone stays `rounding` (decision 50).
- `sign_convention`: the two describe the same change with opposite signs, and any other gap is rounding or a parser miss.

## Rules fixed before check1

- FinQA conventions are not errors: a percentage as a fraction in the program, amounts in the report's own units, a decline answered as a positive size.
- `wrong_side`: `program` when the written answer matches the right answer, `answer` when the program does, `both` when neither does, `question_ambiguous` when each follows a different defensible reading or the report cannot answer the question.
- `error_type` is the first thing to fix on the wrong side, read from the first step. Under `both` it describes the program; name the answer's slip in the note (decision 49), so `answer_typo` and `missing_answer` go with `answer` only. An answer-side type other than `answer_typo` or `missing_answer` is used only when that slip reproduces the written value; otherwise `other`.
- An empty written answer is `real_error`, `answer`, `missing_answer`, also when the program is right. So is an `unparsed` answer whose text gives no value (a footnote, a fragment, the question repeated; decision 51); if the text does mean the right value it is `parser_miss`. If the program is wrong too: `both` with the program's error type. Missing answers are counted apart from wrong answers.
- Programs that average by adding 3 and halving (last two steps `add(#k, const_3), divide(#k+1, const_2)`: 44 items, all flagged or unanswered) are coded `step_count` when judged wrong. So are their near-variants: an extra halving before that tail, adding `const_4` or `const_5` then halving, adding `const_3` and never dividing; the note names the variant (decision 52).
- Identical items (same question, answer, program and report; the test split has 9 such pairs) keep a row each, get the same verdict, and both count.
- `missing_x100` was retired: the screen accepts any ×100 or ÷100 difference, so it cannot cause a flag.
- `question_ambiguous` items are left out of the consistent and corrected test views; the official view keeps every item.
- Counts and self-agreement use verdicts as first recorded. A verdict found wrong later is corrected once, in one commit before the final test run, and listed in the write-up.
- No model prediction on a test item is looked at before that item has a verdict.

## Checking a sheet

`python -m finqa_lora.handcheck check1 --validate` lists invalid values (exit code 1) and items
to look at again: a corrected program that does not run or does not give the corrected answer, a
correction that disagrees with the side marked right, and a note with no number from its own
item. It never changes a verdict. `tests/test_handcheck.py` runs the same check on every
committed sheet, so a sheet with an invalid value fails CI.

## Counting

`python -m finqa_lora.auditcounts` counts each sheet that is finished (a verdict on every row,
nothing invalid, exactly the items it was built with) and only reports progress for the others. The
definitions were fixed on 19 Nov 2026, before any sheet had a verdict:

- `uncertain` rows are left out of every count and reported by number.
- A `real_error` counts as a wrong program when `wrong_side` is `program` or `both`; as a wrong
  written answer when it is `answer` or `both` and the type is not `missing_answer`; empty answers
  and `question_ambiguous` are counted on their own.
- check1: every share with a 95% Wilson interval, also scaled to the 431 train flags. Precision is
  `real_error` over the counted rows. Parser misses are listed; parser v1 stays whatever they show.
- check2 covers every flagged test item, so its counts are exact for the test set; screen precision
  on test `disagree` items gets a Wilson interval.
- check3: misses with an exact one-sided 95% upper bound, also scaled to the 1,040 test `agree` items.
- The 9 `sign_only` test items are in no check and are left out of the test-set totals.

## Test gate

No model generates on the test split until check2 and check3 have a verdict on every row, pass
`--validate` with no invalid value, still hold exactly the items they were built with, and are
committed with no later changes (`finqa_lora/testgate.py`, called by `finqa_lora.infer`). Each test
pass stores the git blob and last commit of both sheets. `python -m finqa_lora.testgate` shows
whether the gate is open.

## Self-agreement

At least a week after the last check, re-check 20 items blind (about 10 `real_error` and 10
others, drawn by code with a fixed seed) in a fresh sheet that shows the item only, and report
how often the two verdicts match.

Fixed by Prit on 22 Nov 2026, before the draw (decision 54; `finqa_lora/recheck.py`):

- **Population:** every row of check1, check2 and check3 that is not `uncertain` in the first pass:
  192 of 198 (131 `real_error`, 61 other verdicts). The 6 uncertain rows are skipped because the
  agreement count leaves them out anyway.
- **Draw:** `random.Random(20261127)`: exactly 10 of the `real_error` ids and then 10 of the others,
  each from the sorted ids; the 20 are then shuffled with the same generator, so the sheet order does
  not show the strata.
- **Sheet:** `recheck.csv` has the columns of the first-pass sheets with the verdict columns empty;
  `recheck.md` gives the same context the first pass had. Neither shows a first verdict, a note or the
  sheet an item came from. The screen status is shown, as it was in the first pass. Same rules as the
  first pass (decision guide, decisions 27-31 and 49-52); `uncertain` is allowed.
- **When and how:** planned for no earlier than 27 Nov 2026, a week after check3 (20 Nov). Changed by
  Prit on 22 Nov 2026, before any verdict (decision 55): the re-check is done on 22 Nov, **two days**
  after the last first-pass verdicts, so that the project is finished before the resume goes out. The
  shorter gap is reported with the result; it makes remembered verdicts more likely, which would raise
  the agreement. In a text editor, without opening `check1.csv`, `check2.csv` or `check3.csv`. `python -m finqa_lora.recheck --validate`
  before committing; the verdicts go in their own commit, after the sheet's build commit is pushed.
- **Counts** (`--counts`, `results/audit/self_agreement.json`): the definition fixed in S7 in
  `auditcounts.agreement`: same verdict, with a 95% Wilson interval and Cohen's kappa, on the five
  verdicts and on `real_error` versus not; rows uncertain in either pass left out; every changed verdict
  listed. The counts refuse a sheet that is unfinished, invalid, uncommitted or committed before 22 Nov.
  The first-pass sheets are pinned by SHA-256 in `tests/test_recheck.py`, so the baseline cannot move.

## Tagging the `other` failures (decision 53)

`errortags` tags every wrong prediction by rule (decision 48); its last tag, `other`, is "anything else",
so the rules do not say why those predictions failed. `tag_other.csv` is a hand-tag sheet for a random
sample of them. Fixed on 21 Nov 2026, after the test run was recorded and before any test prediction on
this sheet was read for tagging:

- **Population:** the distinct test items on which at least one of the 10 adapters (5 cleaned, 5 random)
  has a failure the rules tagged `other` in `results/test/run1`: 266 items. The base-model passes are not in it.
- **Sample:** 50 items, `random.Random(20261120).sample` of the sorted ids, sorted by id. Each row shows one
  prediction: the adapter pass is chosen at random, by the same generator, among the adapters whose prediction
  on that item was tagged `other` (`other_passes` says how many of the 10 that is). The sample describes
  items, not failures, and one prediction per item.
- **Read-only columns** are the item as in the check sheets, `checked` (what check2 or check3 decided about
  the gold label of this item, empty if neither covers it), the shown pass and its program and value.
- **Columns to fill:** `tag` and `note`. There is no `uncertain` column; `unclear` is the way out.

Tags, first that holds (the vocabulary comes from the dev failures tagged `other`, not from test):

| Tag | Holds when |
| --- | --- |
| `gold_wrong` | the gold program is wrong, the question is ambiguous or unanswerable, or the prediction would be right under the correct label. The note says what is right. See the rule under the table for a wrong written answer |
| `invented_number` | the program uses a number that is nowhere in the report and is not a constant |
| `wrong_quantity` | the numbers come from the report, but the program computes another quantity than the question asks: another entity, year or measure, a wrong base or denominator, or a stated figure for something else used as if it answered the question |
| `missing_step` | the right quantity, but a needed step or term is absent: no scale step, no change step, years or items left out of a sum or an average |
| `extra_step` | the right quantity, plus steps the question does not need |
| `wrong_constant` | the right structure, but a wrong `const_*`, divisor or scale |
| `unclear` | none of the above, or the reason cannot be told |

A wrong gold program counts as unanswerable as scored, because a correct prediction would also fail against
it, so it is `gold_wrong`. When only the written answer is wrong and the gold program is right, the failure is
the model's: tag its own reason and say in the note that the written answer is also wrong (scoring is against
the program's result, so this is a real model error). Decided by Prit on 21 Nov 2026, before any tag, and
applied in the tags; it reached the repo one commit after them, because `a62be1a` was committed with the
earlier wording. `a62be1a` also holds the sheet and the tags together. The sample does not depend on that
order: it is drawn by code from the committed run, and `tests/test_othertags.py` draws it again.

`note` is one line: what the prediction does, and the right calculation with its numbers. Work out the
right answer from the question and the report first, then read the prediction.

Three worked examples, from dev (never hand-checked); each prediction was tagged `other` on dev:

| Item | Gold | Prediction | Tag and note |
| --- | --- | --- | --- |
| `UNP/2014/page_35.pdf-2`: cost per car of the 2012 locomotive buyout | `multiply(75, const_1000000), divide(#0, 165)` = 454,545 | `divide(75, 165)` = 0.45455 | `missing_step`: drops the million scale. Right: 75 x 1,000,000 / 165 = 454,545. |
| `PM/2017/page_38.pdf-3`: percentage increase in interest expense | `subtract(914, 23), divide(23, #0)` = 0.02581 | `divide(23, 914)` = 0.02516 | `wrong_quantity`: uses the current-year 914 as the base. The increase is on the prior year: 914 - 23 = 891, 23 / 891 = 2.6%. |
| `DVN/2014/page_85.pdf-1`: average amortization 2015-2019 | `multiply(45, const_4), add(#0, 44), divide(#1, const_5)` = 44.8 | `add(45, 45), add(#0, 44), divide(#1, const_3)` = 44.667 | `missing_step`, not `wrong_constant`: the divisor 3 fits the three terms it sums; the failure is leaving out two of the five years. Right: (4 x 45 + 44) / 5 = 44.8. |

Check a filled sheet with `python -m finqa_lora.othertags --validate` (exit 1 on an invalid value; it lists
notes with no number from their own item for a second look). `tests/test_othertags.py` checks the committed
sheet against a fresh draw from the committed run, so a changed read-only column fails CI.

Counts are fixed now, before any tag: `python -m finqa_lora.othertags --counts` needs a tag on every row and
nothing invalid, and writes `results/errors/other_tags.json`: per tag the items, the share of the 50 with a 95%
Wilson interval, and the same share scaled to the 266 items of the population. These are shares of items with
a failure tagged `other` by at least one adapter, not shares of all failures, and the write-up says so.

`gold_wrong` tags are not audit verdicts. They were made with a model prediction in view, against the rule
that no prediction on a test item is looked at before the item has a verdict, so they stay out of
`results/audit/counts.json` and are reported apart, as label problems seen during error analysis.
