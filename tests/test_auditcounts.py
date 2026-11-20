"""Audit counts on made-up verdicts. No sheet had a verdict when these were written (S7): every
verdict here is constructed, and each expected number is worked out in the test, not read back."""
import csv
import math

import pytest

from finqa_lora import auditcounts, handcheck
from finqa_lora.data import load_split


def make_row(ex, split, status, spec):
    """A valid filled row. spec: (verdict[, wrong_side[, error_type]][, 'uncertain'])."""
    row = {"item": "", **handcheck.read_only_values(ex, split, status)}
    row.update({k: "" for k in handcheck.VERDICT_COLUMNS})
    if spec is None:
        return row
    v = ex["qa"]["exe_ans"]
    exe = format(v, "f").rstrip("0").rstrip(".") if isinstance(v, float) else str(v)   # 2e-05 -> 0.00002
    row.update(verdict=spec[0], note=f"Program gives {exe}.")
    if spec[0] == "real_error":
        side = spec[1]
        row["wrong_side"] = side
        if side != "question_ambiguous":
            row["error_type"] = spec[2] if len(spec) > 2 and spec[2] != "uncertain" else "other"
            row["corrected_answer"] = exe
            if side in ("program", "both"):
                row["corrected_program"] = ex["qa"]["program"]
    if spec[-1] == "uncertain":
        row["uncertain"] = "true"
    return row


def write_sheet(tmp_path, check, spec_for):
    """spec_for(n, ex, status) -> spec or None (no verdict). Returns (path, rows)."""
    split = handcheck.CHECKS[check][0]
    items, _, status = handcheck.select_items(check)
    rows = []
    for n, ex in enumerate(items, 1):
        r = make_row(ex, split, status[ex["id"]], spec_for(n, ex, status[ex["id"]]))
        r["item"] = n
        rows.append(r)
    path = tmp_path / f"{check}.csv"
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=handcheck.SHEET_COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    assert not handcheck.validate(check, path)["invalid"], "the made-up sheet must be valid"
    return path, rows


# check1: 50 rows cycling through 10 specs, so each spec appears exactly 5 times.
CHECK1 = [("real_error", "program", "wrong_number"), ("real_error", "program", "step_count"),
          ("real_error", "answer", "answer_typo"), ("real_error", "both", "wrong_operation"),
          ("real_error", "question_ambiguous"), ("parser_miss",), ("rounding",), ("sign_convention",),
          ("no_error",), ("real_error", "program", "wrong_number", "uncertain")]


def test_upper_bound_is_exact_clopper_pearson():
    assert auditcounts.upper_bound(0, 50) == pytest.approx(1 - 0.05 ** (1 / 50))          # 5.8%: "about 6%"
    # P(X <= k | n, bound) = 5% at the bound, by direct summation
    for k in (1, 2, 5, 17):
        p = auditcounts.upper_bound(k, 50)
        assert sum(math.comb(50, i) * p ** i * (1 - p) ** (50 - i) for i in range(k + 1)) == pytest.approx(0.05)
    assert auditcounts.upper_bound(50, 50) == 1.0
    beta = pytest.importorskip("scipy.stats").beta
    for k in (0, 1, 2, 5):
        assert auditcounts.upper_bound(k, 50) == pytest.approx(beta.ppf(0.95, k + 1, 50 - k), rel=1e-9)


def test_kinds_of_each_side():
    k = lambda side, etype="other", answer="12.5": auditcounts.kinds(
        {"wrong_side": side, "error_type": etype, "answer": answer})
    assert k("program") == {"wrong_program"}
    assert k("answer") == {"wrong_written_answer"}
    assert k("answer", "missing_answer", "") == {"missing_answer"}
    assert k("answer", "missing_answer", "[6] : in 2015 , 2014") == {"missing_answer"}   # decision 51
    assert k("both", "wrong_number") == {"wrong_program", "wrong_written_answer"}
    # decision 49: under both the type is the program's, so an empty answer is read from the answer
    assert k("both", "wrong_number", "") == {"wrong_program", "missing_answer"}
    assert k("question_ambiguous", "") == {"ambiguous"}


def test_check1_counts(tmp_path):
    path, _ = write_sheet(tmp_path, "check1", lambda n, ex, st: CHECK1[(n - 1) % 10])
    c = auditcounts.count_all({"check1": path, "check2": tmp_path / "none.csv", "check3": tmp_path / "none.csv"})
    assert c["sheets"]["check1"]["state"] == "complete"
    k = c["check1"]
    assert (k["rows"], k["uncertain"], k["counted"], k["pool"]) == (50, 5, 45, 431)
    # real_error: 5 specs x 5 rows = 25 (the uncertain sixth is out); program 10 + both 5 = 15 wrong programs
    assert k["precision"]["count"] == 25 and k["precision"]["of"] == 45
    assert {x: k["kinds"][x]["count"] for x in auditcounts.KINDS} == \
        {"wrong_program": 15, "wrong_written_answer": 10, "missing_answer": 0, "ambiguous": 5}
    assert {v: k["verdicts"][v]["count"] for v in handcheck.VERDICTS} == \
        {"real_error": 25, "no_error": 5, "parser_miss": 5, "rounding": 5, "sign_convention": 5}
    assert k["wrong_side"] == {"answer": 5, "both": 5, "program": 10, "question_ambiguous": 5}
    assert k["error_type"] == {"answer_typo": 5, "step_count": 5, "wrong_number": 5, "wrong_operation": 5}
    wp = k["kinds"]["wrong_program"]
    assert wp["share"] == pytest.approx(15 / 45) and wp["in_pool"] == pytest.approx(15 / 45 * 431)
    assert (wp["wilson_low"], wp["wilson_high"]) == pytest.approx(auditcounts.stats.wilson(15, 45))
    assert len(k["parser_misses"]) == 5 and all(p["note"] for p in k["parser_misses"])
    assert "check2" not in c and "test_set" not in c


def test_unfinished_or_changed_sheets_are_not_counted(tmp_path):
    half, _ = write_sheet(tmp_path, "check1", lambda n, ex, st: CHECK1[0] if n <= 20 else None)
    c = auditcounts.count_all({"check1": half, "check2": tmp_path / "x.csv", "check3": tmp_path / "x.csv"})
    assert c["sheets"]["check1"] == {"rows": 50, "with_verdict": 20, "invalid": 0, "state": "in progress"}
    assert "check1" not in c and c["sheets"]["check2"]["state"] == "missing"
    # a sheet missing one of its items is invalid, even with a verdict on every row
    full, rows = write_sheet(tmp_path, "check1", lambda n, ex, st: ("no_error",))
    with open(full, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=handcheck.SHEET_COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows[1:])
    assert auditcounts.read_rows("check1", full)[0]["state"] == "invalid"
    # an invalid value is invalid too
    bad = tmp_path / "bad.csv"
    text = open(write_sheet(tmp_path, "check1", lambda n, ex, st: ("no_error",))[0], encoding="utf-8-sig").read()
    open(bad, "w", encoding="utf-8-sig", newline="").write(text.replace(",no_error,", ",fine,", 1))
    assert auditcounts.read_rows("check1", bad)[0]["state"] == "invalid"


def check2_spec(n, ex, status):
    if status == "no_answer":                      # 14 items: missing answers, some with a wrong program too
        return ("real_error", "both", "wrong_number") if n % 5 == 0 else ("real_error", "answer", "missing_answer")
    if status == "unparsed":                       # 8 items
        return ("parser_miss",)
    return [("real_error", "program", "wrong_number"), ("real_error", "answer", "answer_typo"),
            ("no_error",), ("rounding", "uncertain")][n % 4]


def test_check2_check3_and_the_test_set(tmp_path):
    p2, rows2 = write_sheet(tmp_path, "check2", check2_spec)
    p3, _ = write_sheet(tmp_path, "check3", lambda n, ex, st: ("real_error", "program") if n in (7, 30) else ("no_error",))
    c = auditcounts.count_all({"check1": tmp_path / "none.csv", "check2": p2, "check3": p3})
    k = c["check2"]
    status = {r["id"]: r["screen_status"] for r in rows2}
    assert sorted(collections_count(status.values()).items()) == [("disagree", 76), ("no_answer", 14), ("unparsed", 8)]
    specs = [check2_spec(int(r["item"]), None, r["screen_status"]) for r in rows2]
    dis = [s for s, r in zip(specs, rows2) if r["screen_status"] == "disagree"]
    unc = sum(s[-1] == "uncertain" for s in specs)
    real_dis = sum(s[0] == "real_error" for s in dis)
    both_missing = sum(s[1] == "both" for s, r in zip(specs, rows2) if r["screen_status"] == "no_answer")
    assert k["uncertain"] == unc and k["counted"] == 98 - unc
    assert k["by_status"]["disagree"]["precision"]["count"] == real_dis
    assert k["by_status"]["disagree"]["precision"]["of"] == 76 - unc
    assert k["by_status"]["no_answer"]["kinds"]["missing_answer"]["count"] == 14
    assert k["kinds"]["wrong_program"]["count"] == sum(s[:2] == ("real_error", "program") for s in dis) + both_missing
    assert k["by_status"]["unparsed"]["verdicts"]["parser_miss"]["count"] == 8
    m = c["check3"]["misses"]
    assert (m["count"], m["of"], m["pool"]) == (2, 50, 1040)
    assert m["in_pool_upper"] == pytest.approx(auditcounts.upper_bound(2, 50) * 1040)
    t = c["test_set"]
    assert t["confirmed"] == real_dis + 14 + 2
    assert t["estimate"] == pytest.approx(real_dis + 14 + 2 / 50 * 1040)
    assert t["not_covered"] == {"sign_only": 9, "uncertain": unc}
    assert "check2" in auditcounts.markdown(c) and "upper bound" in auditcounts.markdown(c)


def collections_count(values):
    out = {}
    for v in values:
        out[v] = out.get(v, 0) + 1
    return out


def test_averaging_template_counts_are_pinned():
    a = auditcounts.averaging_template()
    assert {s: a[s]["items"] for s in a} == {"train": 34, "dev": 8, "test": 2}       # 44 (S3)
    assert a["train"]["status"] == {"disagree": 33, "no_answer": 1}
    assert a["dev"]["status"] == {"disagree": 8} and a["test"]["status"] == {"disagree": 2}
    # the rule is the last two steps, so the dev program that starts with subtract and the test
    # program with an extra halving step are in; a plain add(const_3, const_2) is not
    progs = {ex["id"]: ex["qa"]["program"] for s in ("dev", "test") for ex in load_split(s)}
    assert any(p.startswith("subtract(") and auditcounts.is_averaging(p) for p in progs.values())
    assert auditcounts.is_averaging("add(1, 2), add(#0, 3), add(#1, const_3), divide(#2, const_2)")
    assert not auditcounts.is_averaging("add(const_3, const_2)")
    # halving something other than the step that added 3 is a different program
    assert not auditcounts.is_averaging("add(1, 2), add(#0, 3), add(#1, const_3), divide(#1, const_2)")


def test_agreement_and_kappa():
    def rows(verdicts, unc=()):
        return {f"i{n}": {"verdict": v, "uncertain": "true" if n in unc else ""} for n, v in enumerate(verdicts)}
    R, N, P = "real_error", "no_error", "parser_miss"
    a = auditcounts.agreement(rows([R, R, R, R, N, N, N, N, N, N]), rows([R, R, R, N, N, N, N, N, N, R]))
    # observed 8/10; chance (0.4 * 0.4 + 0.6 * 0.6) = 0.52; kappa = 0.28 / 0.48
    assert a["real_error"]["count"] == 8 and a["real_error"]["kappa"] == pytest.approx(0.28 / 0.48)
    assert a["verdict"]["kappa"] == pytest.approx(0.28 / 0.48)
    b = auditcounts.agreement(rows([R, N, P, N]), rows([R, P, P, N], unc={3}))
    # item 3 uncertain in the second pass: 3 items, 2 same verdicts; real_error vs not: 3 of 3
    assert b["items"] == 3 and b["left_out_uncertain"] == 1
    assert b["verdict"]["count"] == 2 and b["real_error"]["count"] == 3 and b["real_error"]["kappa"] == 1.0
    sk = pytest.importorskip("sklearn.metrics")
    assert a["verdict"]["kappa"] == pytest.approx(sk.cohen_kappa_score([R, R, R, R, N, N, N, N, N, N],
                                                                       [R, R, R, N, N, N, N, N, N, R]))


def test_counts_run_on_the_committed_sheets():
    c = auditcounts.count_all()
    assert set(c["sheets"]) == {"check1", "check2", "check3"}
    assert all(s["state"] in ("missing", "invalid", "not started", "in progress", "complete") for s in c["sheets"].values())
    assert all(s["state"] != "invalid" for s in c["sheets"].values())
