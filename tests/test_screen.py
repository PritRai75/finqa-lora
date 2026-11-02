"""The answer parser reads what it should, and the screen counts stay pinned."""
import pytest

from finqa_lora.data import load_split
from finqa_lora.screen import compare, parse_answer, screen_item


@pytest.mark.parametrize("raw, value, decimals", [
    ("380", 380.0, 0),
    ("8.6%", 8.6, 1),
    ("$ 1,234.5 million", 1234.5, 1),
    (".43", 0.43, 2),
    ("-.5%", -0.5, 1),
    ("33.%", 33.0, 0),
    ("431.7\\n", 431.7, 1),
    ("12 .", 12.0, 0),
    ("( $ 98.9 )", -98.9, 1),
    ("yes", "yes", None),
])
def test_parse_answer_reads(raw, value, decimals):
    assert parse_answer(raw) == (value, decimals)


@pytest.mark.parametrize("raw", ["increased 9.9%", "2009-2010", "1.2:1", "$ 3 or $ 3.5 million"])
def test_parse_answer_leaves_free_text_unread(raw):
    assert parse_answer(raw) == (None, None)


@pytest.mark.parametrize("exe, raw, status", [
    (3.8, "380", "agree"),            # fraction written as a percent: x100 is allowed
    (0.086, "8.6%", "agree"),
    (2.6, "8.6%", "disagree"),        # wrong operation in the program
    (-0.05, "5%", "sign_only"),       # decline written as a positive number
    (0.42457, ".43", "disagree"),     # off by rounding: left for the hand-check
    ("no", "yes", "disagree"),
    (1.0, "", "no_answer"),
    (1.0, "increased 9.9%", "unparsed"),
])
def test_compare(exe, raw, status):
    assert compare(exe, raw) == status


# Measured 3 Nov 2026 with parser v1 on commit 0f16e28. A change here is a change in the audit.
PINNED = {
    "train": {"agree": 5656, "disagree": 431, "sign_only": 63, "unparsed": 53, "no_answer": 48},
    "dev": {"agree": 803, "disagree": 57, "sign_only": 8, "unparsed": 3, "no_answer": 12},
    "test": {"agree": 1040, "disagree": 76, "sign_only": 9, "unparsed": 8, "no_answer": 14},
}


@pytest.mark.parametrize("split", sorted(PINNED))
def test_screen_counts_are_pinned(split):
    counts = {}
    for ex in load_split(split):
        s = screen_item(ex)
        counts[s] = counts.get(s, 0) + 1
    assert counts == PINNED[split]
