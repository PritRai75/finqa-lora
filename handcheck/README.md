# Hand-check protocol

Every verdict in this folder is made by hand by the repo author. Code only builds the sheets
(`python -m finqa_lora.handcheck check1`) and later counts the filled columns.

## The three checks

| Check | Items | What it measures |
| --- | --- | --- |
| check1 | 50 random train items the screen flagged (`disagree`) | Precision of the screen, and how many flags are a wrong program rather than a wrong written answer |
| check2 | Every test item that is `disagree`, `unparsed` or `no_answer` | Confirmed test-set errors, by wrong side |
| check3 | 50 random test items the screen passed (`agree`) | An upper bound on the errors the screen misses |

Read each item in `<check>.md` and record the verdict in the matching row of `<check>.csv`.

## Columns to fill

| Column | Values |
| --- | --- |
| `verdict` | `real_error`, `no_error`, `parser_miss`, `sign_convention`, `rounding` |
| `wrong_side` | Only for `real_error`: `program`, `answer`, `both`, `question_ambiguous` |
| `error_type` | Only for `real_error`: `wrong_operation`, `wrong_number`, `operand_order`, `missing_x100`, `wrong_table_row`, `step_count`, `other` |
| `corrected_answer` | The right answer, when `real_error` |
| `corrected_program` | The right program in FinQA syntax, when the program is wrong |
| `uncertain` | `true` if you cannot decide. The item is then left out of every count |
| `note` | One line on why |

Meaning of each verdict:
- `real_error` the program, the written answer or the question is wrong.
- `no_error` both are right (mainly for check3).
- `parser_miss` the screen misread the written answer and the two actually agree.
- `sign_convention` a decline written as a positive number.
- `rounding` the two differ only by rounding of the written answer.

## Self-agreement

At least a week after finishing, re-check about 20 items blind (mix of `real_error` and others)
in a fresh copy of the sheet, and report how often the two verdicts match.
