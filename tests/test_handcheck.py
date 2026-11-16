"""The hand-check validator accepts sheets that follow the protocol and lists every kind of slip.

Examples use dev items, which are never hand-checked.
"""
import pytest

from finqa_lora import handcheck
from finqa_lora.data import load_split

DEV = {ex["id"]: ex for ex in load_split("dev")}
ETR = "ETR/2011/page_341.pdf-3"   # program adds 0.3 where the table shows (0.3); written 18.6
LMT = "LMT/2015/page_56.pdf-3"    # program 19700; written 197000


def row(item_id, **verdict):
    ex = DEV[item_id]
    r = {"item": "1"} | handcheck.read_only_values(ex, "dev", "disagree")
    r.update({k: "" for k in handcheck.VERDICT_COLUMNS})
    r.update(verdict)
    return r, ex


PROGRAM_WRONG = dict(verdict="real_error", wrong_side="program", error_type="wrong_number",
                     corrected_answer="18.6", corrected_program="subtract(18.9, 0.3)",
                     note="Program adds 0.3 but the table shows (0.3). Right: 18.9 - 0.3 = 18.6.")
ANSWER_WRONG = dict(verdict="real_error", wrong_side="answer", error_type="answer_typo",
                    corrected_answer="19700", note="Answer has an extra zero. Program right: 19700.")


def test_allowed_values_are_pinned():
    assert handcheck.VERDICTS == ("real_error", "no_error", "parser_miss", "rounding", "sign_convention")
    assert handcheck.WRONG_SIDES == ("program", "answer", "both", "question_ambiguous")
    assert handcheck.ERROR_TYPES == ("wrong_number", "wrong_table_row", "wrong_operation", "operand_order",
                                     "step_count", "scale_or_units", "answer_typo", "missing_answer", "other")
    assert "missing_x100" not in handcheck.ERROR_TYPES   # retired on 10 Nov 2026


@pytest.mark.parametrize("item_id, verdict", [(ETR, PROGRAM_WRONG), (LMT, ANSWER_WRONG),
                                              (LMT, dict(verdict="rounding", note="19700 written as 197000."))])
def test_valid_rows_pass_clean(item_id, verdict):
    assert handcheck.check_row(*row(item_id, **verdict)) == ([], [])


def test_empty_row_is_not_checked():
    assert handcheck.check_row(*row(ETR)) == ([], [])


@pytest.mark.parametrize("item_id, change, message", [
    (ETR, dict(verdict="Real_error"), "verdict 'Real_error' not in"),
    (ETR, dict(wrong_side="programme"), "wrong_side 'programme' not in"),
    (ETR, dict(error_type="missing_x100"), "error_type 'missing_x100' not in"),
    (ETR, dict(error_type="answer_typo"), "needs wrong_side answer or both"),
    (ETR, dict(uncertain="yes"), "uncertain 'yes'"),
    (ETR, dict(note=""), "note is empty"),
    (ETR, dict(corrected_answer=""), "corrected_answer is empty"),
    (ETR, dict(corrected_answer="about 18"), "cannot be read"),
    (ETR, dict(corrected_program=""), "corrected_program is empty"),
    (ETR, dict(corrected_program="subtrac(18.9, 0.3)"), "does not run"),
    (LMT, dict(error_type="missing_answer"), "the item has a written answer"),
    (LMT, dict(corrected_program="add(1, 2)"), "must be empty when only the answer is wrong"),
])
def test_invalid_values_are_listed(item_id, change, message):
    base = PROGRAM_WRONG if item_id == ETR else ANSWER_WRONG
    invalid, _ = handcheck.check_row(*row(item_id, **(base | change)))
    assert any(message in m for m in invalid), invalid


def test_columns_must_stay_empty_unless_real_error():
    invalid, _ = handcheck.check_row(*row(LMT, verdict="rounding", wrong_side="answer", note="19700 vs 197000."))
    assert invalid == ["wrong_side must be empty unless verdict is real_error"]


def test_question_ambiguous_takes_no_correction():
    ok = dict(verdict="real_error", wrong_side="question_ambiguous", note="Ambiguous: 18.9 or 18.6.")
    assert handcheck.check_row(*row(ETR, **ok)) == ([], [])
    invalid, _ = handcheck.check_row(*row(ETR, **(ok | dict(corrected_answer="18.6"))))
    assert invalid == ["corrected_answer must be empty for question_ambiguous"]


def test_shifted_rows_are_caught():
    r, _ = row(ETR, **PROGRAM_WRONG)
    invalid, _ = handcheck.check_row(r, DEV[LMT])
    assert any("read-only column question changed" in m for m in invalid)


@pytest.mark.parametrize("column, saved", [("answer", "18.60"), ("exe_ans", "19"), ("program", "add(18.9,0.3)")])
def test_spreadsheet_rewrites_are_caught_even_without_a_verdict(column, saved):
    """Excel rewrote check1.csv on 16 Nov: 43.9% -> 43.90%, 0.0 -> 0. Empty rows must be checked too."""
    r, ex = row(ETR)
    r[column] = saved
    invalid, _ = handcheck.check_row(r, ex)
    assert invalid == [f"read-only column {column} changed: sheet {saved!r}, item {r_ro(ex)[column]!r} "
                       "(saved by a spreadsheet? restore it with git restore)"]


def r_ro(ex):
    return handcheck.read_only_values(ex, "dev", "disagree")


def test_committed_sheet_matches_the_data_on_every_row():
    """build() and validate() agree: a sheet built today passes the read-only check unchanged."""
    report = handcheck.validate("check1")
    assert not [m for m in report["invalid"] if "read-only" in m[2] or "header" in m[2]]


@pytest.mark.parametrize("change, message", [
    (dict(corrected_program="subtract(18.9, 0.4)"), "does not match corrected_answer"),
    (dict(note="Program uses the wrong year: 4,321 not 9,876."), "no number from its own item"),
])
def test_inconsistencies_are_listed_for_review(change, message):
    invalid, review = handcheck.check_row(*row(ETR, **(PROGRAM_WRONG | change)))
    assert invalid == [] and any(message in m for m in review), review


def test_answer_side_correction_must_match_the_program():
    _, review = handcheck.check_row(*row(LMT, **(ANSWER_WRONG | dict(corrected_answer="19800"))))
    assert any("differs from the program result" in m for m in review)


@pytest.mark.parametrize("check", [c for c in handcheck.CHECKS if (handcheck.OUT / f"{c}.csv").exists()])
def test_committed_sheets_have_no_invalid_values(check):
    """Gate: verdicts can only be committed when every filled value follows the protocol."""
    report = handcheck.validate(check)
    assert report["invalid"] == [], report["invalid"]
