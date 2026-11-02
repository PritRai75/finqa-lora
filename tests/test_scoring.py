"""The scoring wrapper gives the official results on gold programs and survives bad predictions."""
import pytest

from finqa_lora import SPLITS
from finqa_lora.data import load_split
from finqa_lora.scoring import exe_correct, execute, prog_correct

DATA = {s: load_split(s) for s in SPLITS}
EXPECTED_SIZES = {"train": 6251, "dev": 883, "test": 1147}


@pytest.mark.parametrize("split", SPLITS)
def test_split_sizes(split):
    assert len(DATA[split]) == EXPECTED_SIZES[split]


@pytest.mark.parametrize("split", SPLITS)
def test_every_gold_program_reproduces_exe_ans(split):
    wrong = [ex["id"] for ex in DATA[split] if not exe_correct(ex["qa"]["program"], ex)]
    assert wrong == []


@pytest.mark.parametrize("split", ["dev", "test"])
def test_every_gold_program_matches_itself(split):
    wrong = [ex["id"] for ex in DATA[split] if not prog_correct(ex["qa"]["program"], ex)]
    assert wrong == []


def _find(program_start):
    return next(ex for ex in DATA["dev"] if ex["qa"]["program"].startswith(program_start))


def test_wrong_operation_is_not_correct():
    ex = _find("subtract(")
    wrong = ex["qa"]["program"].replace("subtract(", "add(", 1)
    assert not exe_correct(wrong, ex)
    assert not prog_correct(wrong, ex)


@pytest.mark.parametrize("bad", ["", "nonsense", "divide(1, 0)", "add(#3, 2)", "subtract(5829, 5735",
                                 "table_sum(no such row, none)"])
def test_malformed_predictions_score_wrong_without_crashing(bad):
    ex = DATA["dev"][0]
    assert not exe_correct(bad, ex)
    assert not prog_correct(bad, ex)
    assert execute(bad, ex["table"])[0] is False


def test_swapped_add_is_same_program():
    # Program accuracy is symbolic: add(a, b) equals add(b, a). Execution accuracy agrees.
    ex = next(e for e in DATA["dev"] if e["qa"]["program"].count("(") == 1
              and e["qa"]["program"].startswith("add("))
    a, b = ex["qa"]["program"][4:-1].split(", ")
    swapped = f"add({b}, {a})"
    assert exe_correct(swapped, ex)
    assert prog_correct(swapped, ex)
