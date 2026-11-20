"""Error tags: one made-up item per tag and per precedence case, then the committed dev predictions."""
import csv
import json

import pytest

from finqa_lora import errortags
from finqa_lora.scoring import execute

TABLE = [["", "2019", "2018"], ["revenue", "$ 100", "90"], ["cost", "40", "30"]]


def item(gold, answer="", table=TABLE):
    ok, value = execute(gold, table)
    assert ok
    return {"id": "x", "table": table, "qa": {"program": gold, "exe_ans": value, "answer": answer}}


def tag(pred, gold, table=TABLE):
    ex = item(gold, table=table)
    ok, value = execute(pred, table) if pred else (False, None)
    return errortags.tag(pred, int(ok), "" if value is None else value, ex)


@pytest.mark.parametrize("pred, gold, want", [
    ("", "subtract(100, 90)", "invalid"),
    ("subtract(100, )", "subtract(100, 90)", "invalid"),
    ("table_sum(profit, none)", "subtract(100, 90)", "invalid"),                    # no such row: does not run
    # same numbers placed differently: a swapped subtract is operand_order, not sign
    ("subtract(90, 100)", "subtract(100, 90)", "operand_order"),
    ("subtract(2383, 1891), divide(#0, 1891)", "subtract(1891, 2383), divide(#0, 2383)", "operand_order"),
    ("divide(const_60, 3)", "divide(3, 60)", "operand_order"),
    # a missing final x100 is scale_x100, not step_count
    ("subtract(100, 90), divide(#0, 90), multiply(#1, const_100)", "subtract(100, 90), divide(#0, 90)", "scale_x100"),
    ("divide(1, 4)", "divide(1, 4), multiply(#0, const_100)", "scale_x100"),
    ("subtract(-33.7, 34.7)", "add(34.7, 33.7)", "sign"),
    ("add(5583333, 5583333), add(#0, 5583334)", "multiply(5583334, const_3)", "near_value"),
    ("divide(66.1, 89.7)", "multiply(66.1, 89.7)", "wrong_operation"),
    ("multiply(89.7, 66.1), add(#0, 2)", "multiply(66.1, 89.7), subtract(#0, 2)", "wrong_operation"),
    ("subtract(40, 90)", "subtract(100, 90)", "wrong_table_row"),                  # 40 is 100's column, other row
    ("table_sum(cost, none)", "table_sum(revenue, none)", "wrong_table_row"),
    ("subtract(77, 90)", "subtract(100, 90)", "wrong_number"),                     # 77 is not in the table
    ("subtract(100, 2018)", "subtract(100, 90)", "wrong_number"),                  # 2018 is 90's column, but the header
    ("subtract(100, 90)", "subtract(100, 90), divide(#0, 90)", "step_count"),
    ("multiply(77.76, 1425)", "multiply(1425, 77.76), multiply(#0, 365)", "step_count"),   # add/multiply either order
    ("add(13, 19), add(#0, 2), divide(#1, const_3)", "subtract(100, 90), divide(#0, 90)", "other"),
])
def test_one_tag_per_failure(pred, gold, want):
    assert tag(pred, gold) == want


def test_every_tag_is_reachable_and_listed():
    assert errortags.TAGS[0] == "invalid" and errortags.TAGS[-1] == "other" and len(set(errortags.TAGS)) == 10


def test_tag_rows_skips_correct_items_and_checks_the_written_answer(monkeypatch):
    ex = item("subtract(100, 90), divide(#0, 90)", answer="11%")       # gold 0.11111; written answer 11%
    ex["id"] = "a"
    monkeypatch.setattr(errortags, "load_split", lambda split: [ex])
    monkeypatch.setattr(errortags, "screen_status", lambda split: {"a": "disagree"})
    rows = [{"id": "a", "program": "subtract(100, 90), divide(#0, 90)", "executes": "1", "value": "0.11111", "exe_correct": "1"},
            {"id": "a", "program": "divide(11, const_100)", "executes": "1", "value": "0.11", "exe_correct": "0"},
            {"id": "a", "program": "divide(40, 30)", "executes": "1", "value": "1.33333", "exe_correct": "0"}]
    out = errortags.tag_rows(rows, "dev")
    assert [t["matches_answer"] for t in out] == [True, False]
    s = errortags.summarise(out)
    assert s["failures"] == 2 and s["on_flagged_items"] == 2 and s["flagged_matching_written_answer"] == 1


def test_dev_tags_cover_every_failure_and_are_pinned():
    summary = errortags.run_dev(write=False)
    assert len(summary) == 14                       # 10 adapters, 2 bases x 2 shot settings
    for name, path in errortags.dev_files().items():
        with open(path, encoding="utf-8", newline="") as f:
            wrong = sum(1 - int(r["exe_correct"]) for r in csv.DictReader(f))
        assert summary[name]["failures"] == wrong == sum(summary[name]["tags"].values())
    # pinned on 19 Nov 2026 (S7), from the committed main run 1 predictions
    assert summary["adapter:cleaned:1"]["tags"] == {
        "invalid": 6, "operand_order": 18, "scale_x100": 19, "sign": 5, "near_value": 1, "wrong_operation": 10,
        "wrong_table_row": 31, "wrong_number": 85, "step_count": 7, "other": 113}
    assert summary["adapter:cleaned:1"]["flagged_matching_written_answer"] == 17


def test_committed_summary_matches_the_code():
    path = errortags.OUT / "dev.json"
    if not path.exists():
        pytest.skip("results/errors/dev.json not committed yet")
    with open(path, encoding="utf-8") as f:
        assert json.load(f) == errortags.run_dev(write=False)
