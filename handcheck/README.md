# Hand-check protocol

Every verdict in this folder is made by hand by the repo author. Code only builds the sheets
(`python -m finqa_lora.handcheck check1`), checks filled sheets (`--validate`) and later counts
the filled columns. The rules below were fixed on 10 Nov 2026, before check1 started.

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
- `rounding`: the written answer is the right value rounded more coarsely than the screen allowed, the report gives the same figure at two precisions, or the gap is under 1% of the right value and no specific calculation explains it.
- `sign_convention`: the two describe the same change with opposite signs, and any other gap is rounding or a parser miss.

## Rules fixed before check1

- FinQA conventions are not errors: a percentage as a fraction in the program, amounts in the report's own units, a decline answered as a positive size.
- `wrong_side`: `program` when the written answer matches the right answer, `answer` when the program does, `both` when neither does, `question_ambiguous` when each follows a different defensible reading or the report cannot answer the question.
- `error_type` is the first thing to fix on the wrong side, read from the first step. An answer-side type other than `answer_typo` or `missing_answer` is used only when that slip reproduces the written value; otherwise `other`.
- An empty written answer is `real_error`, `answer`, `missing_answer`, also when the program is right (`both` if the program is wrong too). These are counted apart from wrong answers.
- Programs following `add(a, b), add(#0, c), add(#1, const_3), divide(#2, const_2)` (44 items, all flagged or unanswered) are coded `step_count` when judged wrong.
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
