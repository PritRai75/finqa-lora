"""The `other` hand-tag sample: the draw is reproducible and matches the rule-based tags, the sheet validator
accepts sheets that follow the protocol and lists every slip, and the counts need a finished sheet.

The committed sheet is checked against a fresh draw from the committed test run (decision 53).
"""
import csv
import json

import pytest

from finqa_lora import errortags, othertags
from finqa_lora.handcheck import screen_status

SHEET = othertags.OUT / f"{othertags.NAME}.csv"


@pytest.fixture(scope="module")
def drawn():
    sample, pool = othertags.draw()
    expected = othertags.sheet_rows(sample, screen_status("test"), othertags.checked_column())
    return sample, pool, expected


def filled_copy(tmp_path, expected, tags, note=None):
    """A copy of the empty sheet with tag and note filled on the first len(tags) rows."""
    path = tmp_path / "tag_other.csv"
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(othertags.SHEET_COLUMNS)
        for i, r in enumerate(expected):
            tag = tags[i] if i < len(tags) else ""
            text = (note or f"Predicted {r['pred_value']}; gold gives {r['exe_ans']}.") if tag else ""
            w.writerow([r[k] for k in othertags.SHEET_COLUMNS if k not in othertags.VERDICT_COLUMNS] + [tag, text])
    return path


def test_design_is_pinned():
    assert (othertags.SEED, othertags.N) == (20261120, 50)
    assert othertags.TAGS == ("gold_wrong", "invented_number", "wrong_quantity", "missing_step", "extra_step",
                              "wrong_constant", "unclear")
    assert othertags.VERDICT_COLUMNS == ["tag", "note"]   # no uncertain column: `unclear` is the way out


def test_pool_is_the_adapter_failures_the_rules_tagged_other(drawn):
    sample, pool, _ = drawn
    failures = othertags.adapter_other_failures()
    assert len(pool) == 266 and pool == sorted(failures)
    # The same failures errortags counted: per adapter pass, `other` in the committed summary.
    committed = json.load(open(errortags.OUT / "test.json", encoding="utf-8"))
    per_pass = {}
    for passes in failures.values():
        for name, _row in passes:
            per_pass[name] = per_pass.get(name, 0) + 1
    assert len(per_pass) == 10 and all(n.startswith("adapter:") for n in per_pass)
    assert per_pass == {n: s["tags"]["other"] for n, s in committed.items() if n.startswith("adapter:")}


def test_draw_is_fifty_distinct_items_from_the_pool_in_id_order(drawn):
    sample, pool, _ = drawn
    ids = [ex["id"] for ex, *_ in sample]
    assert len(ids) == 50 == len(set(ids)) and ids == sorted(ids) and set(ids) <= set(pool)


def test_shown_prediction_is_an_other_failure_of_one_adapter(drawn):
    sample, _, _ = drawn
    failures = othertags.adapter_other_failures()
    for ex, name, row, passes in sample:
        assert name in passes and passes == [n for n, _ in failures[ex["id"]]]
        assert (name, row) in failures[ex["id"]]
        assert int(row["exe_correct"]) == 0


def test_draw_is_reproducible(drawn):
    sample, pool, _ = drawn
    again, pool2 = othertags.draw()
    assert pool2 == pool
    assert [(ex["id"], n) for ex, n, *_ in again] == [(ex["id"], n) for ex, n, *_ in sample]


def test_checked_column_reads_the_frozen_check_sheets():
    c = othertags.checked_column()
    assert len(c) == 98 + 50 and set(v.split(":")[0] for v in c.values()) == {"check2", "check3"}
    assert "check3:no_error" in c.values() and any(v.startswith("check2:real_error:") for v in c.values())


def test_committed_sheet_is_the_draw_and_has_no_invalid_value(drawn):
    assert SHEET.exists() and (othertags.OUT / f"{othertags.NAME}.md").exists()
    rep = othertags.validate()
    assert rep["invalid"] == [] and rep["rows"] == 50 and rep["pool"] == 266


def test_empty_sheet_is_valid_but_unfinished_and_cannot_be_counted(drawn, tmp_path):
    _, _, expected = drawn
    path = filled_copy(tmp_path, expected, [])
    rep = othertags.validate(path)
    assert rep["invalid"] == [] and rep["with_tag"] == 0
    assert othertags.counts(path)[0] is None
    path = filled_copy(tmp_path, expected, ["unclear"] * 49)
    assert othertags.validate(path)["with_tag"] == 49 and othertags.counts(path)[0] is None


def test_counts_of_a_finished_sheet(drawn, tmp_path):
    _, _, expected = drawn
    tags = (["wrong_quantity"] * 20 + ["missing_step"] * 15 + ["gold_wrong"] * 10 + ["unclear"] * 5)
    out, rep = othertags.counts(filled_copy(tmp_path, expected, tags))
    assert rep["invalid"] == [] and out["sample"] == 50 and out["pool"] == 266
    assert {t: v["items"] for t, v in out["tags"].items()} == {
        "gold_wrong": 10, "invented_number": 0, "wrong_quantity": 20, "missing_step": 15, "extra_step": 0,
        "wrong_constant": 0, "unclear": 5}
    q = out["tags"]["wrong_quantity"]
    assert q["share"] == 0.4 and q["pool_estimate"] == round(0.4 * 266)
    assert q["wilson_low"] < 0.4 < q["wilson_high"] and q["pool_low"] < q["pool_estimate"] < q["pool_high"]
    assert out["tags"]["extra_step"]["wilson_low"] < 1e-9 and out["tags"]["extra_step"]["wilson_high"] > 0


@pytest.mark.parametrize("mutate, message", [
    (lambda r: r.update(tag="Missing_step"), "tag 'Missing_step' not in"),
    (lambda r: r.update(tag="other"), "tag 'other' not in"),
    (lambda r: r.update(tag="", note="x"), "note filled but tag empty"),
    (lambda r: r.update(note=""), "note is empty"),
    (lambda r: r.update(question=r["question"] + " "), "read-only column question changed"),
    (lambda r: r.update(pred_program="divide(1, 2)"), "read-only column pred_program changed"),
    (lambda r: r.update(shown_pass="adapter:cleaned:9"), "read-only column shown_pass changed"),
])
def test_every_kind_of_slip_is_listed(drawn, mutate, message):
    sample, _, expected = drawn
    row = dict(expected[0]) | {"tag": "missing_step", "note": f"Gives {expected[0]['pred_value']}."}
    mutate(row)
    invalid, _ = othertags.check_row(row, expected[0], sample[0][0])
    assert any(message in m for m in invalid), invalid


def test_a_note_without_a_number_of_its_item_is_for_review_not_invalid(drawn):
    sample, _, expected = drawn
    row = dict(expected[0]) | {"tag": "unclear", "note": "Drops 987654321 from the sum."}
    invalid, review = othertags.check_row(row, expected[0], sample[0][0])
    assert invalid == [] and len(review) == 1
    row["note"] = f"Gives {expected[0]['pred_value']}."
    assert othertags.check_row(row, expected[0], sample[0][0]) == ([], [])


def test_rows_out_of_order_or_changed_header_are_invalid(drawn, tmp_path):
    _, _, expected = drawn
    path = filled_copy(tmp_path, expected, [])
    lines = path.read_text(encoding="utf-8-sig").splitlines(keepends=True)
    swapped = tmp_path / "swapped.csv"
    swapped.write_text("".join([lines[0], lines[2], lines[1]] + lines[3:]), encoding="utf-8-sig")
    assert "not the 50 items of the draw" in othertags.validate(swapped)["invalid"][0][2]
    renamed = tmp_path / "renamed.csv"
    renamed.write_text(lines[0].replace("pred_value", "value") + "".join(lines[1:]), encoding="utf-8-sig")
    assert "header changed" in othertags.validate(renamed)["invalid"][0][2]


def test_build_never_overwrites_a_sheet(monkeypatch, tmp_path):
    (tmp_path / f"{othertags.NAME}.csv").write_text("item\n1\n")
    monkeypatch.setattr(othertags, "OUT", tmp_path)
    with pytest.raises(SystemExit, match="Not overwriting"):
        othertags.build()
    assert (tmp_path / f"{othertags.NAME}.csv").read_text() == "item\n1\n"
