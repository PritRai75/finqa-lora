"""Test views and statistics on a made-up test run and made-up check2 and check3 verdicts.

No real test prediction exists when these are written (S6): every number here is constructed.
"""
import csv
import json
import subprocess

import pytest

from finqa_lora import handcheck, runlog, testeval
from finqa_lora.data import load_split
from finqa_lora.testpass import all_passes, parse_pass

ITEMS = load_split("test")
STATUS = handcheck.screen_status("test")
WRONG = "subtract(0, 1)"          # runs, gives -1.0, matches no test exe_ans used below
FIXED = "add(1000003, 7)"         # the made-up corrected program: 1000010.0


def test_made_up_programs_behave_as_assumed():
    from finqa_lora.scoring import execute
    assert execute(WRONG, [])[1] == -1.0 and execute(FIXED, [])[1] == 1000010.0
    assert not any(ex["qa"]["exe_ans"] in (-1.0, 1000010.0) for ex in ITEMS)


def fake_sheets(kinds):
    """check2 and check3 rows. kinds: {check: [verdict spec per item, cycled]}."""
    sheets = {}
    for check in ("check2", "check3"):
        items, _, _ = handcheck.select_items(check)
        rows = {}
        for n, ex in enumerate(items):
            spec = kinds[check][n % len(kinds[check])]
            r = {k: "" for k in handcheck.VERDICT_COLUMNS}
            r.update(id=ex["id"], verdict=spec[0])
            if spec[0] == "real_error":
                r["wrong_side"] = spec[1]
                if spec[1] in ("program", "both"):
                    r["corrected_program"] = FIXED
            if len(spec) > 2 and spec[2] == "uncertain":
                r["uncertain"] = "true"
            rows[ex["id"]] = r
        sheets[check] = rows
    return sheets


# check2 (98 items) cycles through 7 kinds; check3 (50 items) has 2 real errors, the rest clean.
KINDS = {"check2": [("no_error",), ("parser_miss",), ("real_error", "program"), ("real_error", "answer"),
                    ("real_error", "both"), ("real_error", "question_ambiguous"), ("rounding", "", "uncertain")],
         "check3": [("real_error", "program")] * 2 + [("no_error",)] * 48}


def counts(sheets):
    v = [r for rows in sheets.values() for r in rows.values()]
    unc = sum(r["uncertain"] == "true" for r in v)
    amb = sum(r["wrong_side"] == "question_ambiguous" and r["uncertain"] != "true" for r in v)
    real = sum(r["verdict"] == "real_error" and r["uncertain"] != "true" for r in v)
    prog = sum(r["wrong_side"] in ("program", "both") and r["uncertain"] != "true" for r in v)
    return unc, amb, real, prog


def write_run(root, program_for, sheets_blob="b" * 40):
    """A run folder as jobs/testpass.sh writes it. program_for(pass_name, ex) -> program string."""
    from finqa_lora.scoring import execute
    run = root / "results" / "test" / "run1"
    for name in all_passes():
        p = parse_pass(name)
        d = run / (f"{p['arm']}/seed{p['seed']}" if p["kind"] == "adapter" else f"base/{p['base']}/{p['shots']}shot")
        d.mkdir(parents=True)
        rows = []
        for ex in ITEMS:
            prog = program_for(name, ex)
            ok, value = execute(prog, ex["table"]) if prog else (False, None)
            rows.append({"id": ex["id"], "reply": prog, "program": prog, "executes": int(ok),
                         "value": "" if value is None else value,
                         "exe_correct": int(bool(prog) and ok and value == ex["qa"]["exe_ans"]),
                         "prog_correct": 0})
        with open(d / "test.csv", "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        summary = {"items": len(rows), **{k: sum(r[k] for r in rows) for k in ("exe_correct", "prog_correct", "executes")},
                   "split": "test", "test_gate": {"check2": {"git_blob": sheets_blob}, "check3": {"git_blob": sheets_blob}}}
        (d / "result.json").write_text(json.dumps({"pass": name, **p, "revision": None, "test": summary,
                                                   "adapter_sha256": "0" * 64 if p["kind"] == "adapter" else None}))
    (run / "report.json").write_text(json.dumps({
        "missing_passes": [], "one_gate_record": True, "dev_checks": [],
        "test_gate": {"check2": {"git_blob": sheets_blob}, "check3": {"git_blob": sheets_blob}},
        "passes": [{"pass": n} for n in all_passes()]}))
    return run


def gold(name, ex):
    return ex["qa"]["program"]


def test_item_rules_follow_the_views_definition():
    sheets = fake_sheets(KINDS)
    rules, reasons = testeval.item_rules(ITEMS, STATUS, sheets)
    unc, amb, real, prog = counts(sheets)
    assert (unc, amb) == (14, 14)                      # 98 / 7 each in check2
    assert reasons["sign_only"] == 9 and reasons["agree"] == 1040 - 50
    consistent = sum(r["consistent"] for r in rules.values())
    corrected = sum(r["corrected"] for r in rules.values())
    assert consistent == 1147 - 9 - unc - real         # real counts question_ambiguous too
    assert corrected == 1147 - unc - amb
    assert sum(r["target"] == 1000010.0 for r in rules.values()) == prog == 14 + 14 + 2
    for i, r in rules.items():                         # everything else keeps exe_ans
        if r["target"] != 1000010.0:
            assert r["target"] == next(ex for ex in ITEMS if ex["id"] == i)["qa"]["exe_ans"]


def test_a_flagged_item_without_a_verdict_stops_the_evaluation():
    sheets = fake_sheets(KINDS)
    first = next(iter(sheets["check2"]))
    sheets["check2"][first]["verdict"] = ""
    with pytest.raises(ValueError, match="no verdict"):
        testeval.item_rules(ITEMS, STATUS, sheets)
    del sheets["check2"][first]
    with pytest.raises(ValueError, match="no check2 verdict"):
        testeval.item_rules(ITEMS, STATUS, sheets)


def test_gold_programs_score_all_official_and_miss_only_the_corrected_items(tmp_path):
    sheets = fake_sheets(KINDS)
    ev = testeval.evaluate(write_run(tmp_path, gold), sheets=sheets, check_gate=False)
    unc, amb, real, prog = counts(sheets)
    a = ev["views"]["official"]["accuracy"]["adapter:cleaned:1"]
    assert (a["correct"], a["items"]) == (1147, 1147)
    c = ev["views"]["corrected"]["accuracy"]["adapter:cleaned:1"]
    assert (c["correct"], c["items"]) == (1147 - unc - amb - prog, 1147 - unc - amb)
    s = ev["views"]["consistent"]["accuracy"]["adapter:cleaned:1"]
    assert s["correct"] == s["items"] == 1147 - 9 - unc - real
    w = ev["views"]["official"]["cleaned_vs_random"]
    assert w["verdict"] == "no detectable difference" and w["difference"] == 0
    assert ev["views"]["official"]["finetuned_vs_base"]["base:qwen3-4b:4"]["verdict"] == "mixed"   # identical: p = 1
    assert (tmp_path / "results" / "test" / "run1" / "evaluation.json").exists()


def test_the_corrected_program_counts_as_right_only_in_the_corrected_view(tmp_path):
    sheets = fake_sheets(KINDS)
    fixed = {i for rows in sheets.values() for i, r in rows.items() if r["corrected_program"] and r["uncertain"] != "true"}
    run = write_run(tmp_path, lambda n, ex: FIXED if ex["id"] in fixed else ex["qa"]["program"])
    ev = testeval.evaluate(run, sheets=sheets, check_gate=False)
    unc, amb, _, _ = counts(sheets)
    assert ev["views"]["official"]["accuracy"]["base:qwen2.5-1.5b:0"]["correct"] == 1147 - len(fixed)
    c = ev["views"]["corrected"]["accuracy"]["base:qwen2.5-1.5b:0"]
    assert c["correct"] == c["items"] == 1147 - unc - amb


def test_rules_declare_winners_only_when_they_should(tmp_path):
    """Cleaned seeds right on 60 more items than random seeds, every seed; bases always wrong."""
    sheets = fake_sheets(KINDS)
    extra = {ex["id"] for ex in ITEMS[:60]}
    noise = {s: {ex["id"] for ex in ITEMS[200 + 7 * s: 210 + 7 * s]} for s in range(1, 6)}

    def program(name, ex):
        p = parse_pass(name)
        if p["kind"] == "base":
            return WRONG
        if ex["id"] in noise[p["seed"]]:                       # seed-specific misses, both arms
            return WRONG
        if p["arm"] == "random" and ex["id"] in extra:
            return WRONG
        return ex["qa"]["program"]

    ev = testeval.evaluate(write_run(tmp_path, program), sheets=sheets, check_gate=False)
    w = ev["views"]["official"]["cleaned_vs_random"]
    assert w["verdict"] == "cleaning helped" and abs(w["difference"] - 60 / 1147) < 1e-12
    for base, r in ev["views"]["official"]["finetuned_vs_base"].items():
        assert r["verdict"] == "fine-tuning beats the base" and r["p_max"] < 1e-100, base
    md = testeval.markdown(ev)
    assert "Cleaned versus random: cleaning helped" in md and "### corrected view" in md


def test_a_stored_score_that_does_not_rescore_stops_the_evaluation(tmp_path):
    run = write_run(tmp_path, gold)
    path = run / "random" / "seed3" / "test.csv"
    text = path.read_text(encoding="utf-8").splitlines()
    head, first = text[0], text[1].rsplit(",", 2)
    text[1] = ",".join([first[0], "0", first[2]])          # exe_correct 1 -> 0 without changing the program
    path.write_text("\n".join(text) + "\n", encoding="utf-8")
    res = json.loads((path.parent / "result.json").read_text())
    res["test"]["exe_correct"] -= 1
    (path.parent / "result.json").write_text(json.dumps(res))
    with pytest.raises(ValueError, match="re-scored 1, stored exe_correct 0"):
        testeval.evaluate(run, sheets=fake_sheets(KINDS), check_gate=False)


def test_an_incomplete_run_is_refused(tmp_path):
    run = write_run(tmp_path, gold)
    rep = json.loads((run / "report.json").read_text())
    rep["missing_passes"] = ["base:qwen3-4b:4"]
    (run / "report.json").write_text(json.dumps(rep))
    with pytest.raises(SystemExit, match="missing passes"):
        testeval.evaluate(run, sheets=fake_sheets(KINDS), check_gate=False)


def git(root, *args):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "core.autocrlf=false", *args],
                          cwd=root, check=True, capture_output=True, text=True).stdout.strip()


def test_sheets_changed_after_the_test_passes_are_refused(tmp_path):
    git(tmp_path, "init", "-q")
    (tmp_path / "handcheck").mkdir()
    for c in ("check2", "check3"):
        (tmp_path / "handcheck" / f"{c}.csv").write_text(f"{c} verdicts\n")
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-q", "-m", "v")
    gate = {c: {"git_blob": git(tmp_path, "rev-parse", f"HEAD:handcheck/{c}.csv")} for c in ("check2", "check3")}
    testeval.sheets_match_gate(gate, root=tmp_path)
    (tmp_path / "handcheck" / "check3.csv").write_text("check3 verdicts, edited\n")
    git(tmp_path, "commit", "-q", "-am", "edit")
    with pytest.raises(SystemExit, match="check3.csv changed since the test passes ran"):
        testeval.sheets_match_gate(gate, root=tmp_path)


def test_runlog_indexes_a_test_run(tmp_path):
    write_run(tmp_path, gold)
    counts_ = runlog.build(db=tmp_path / "runs.db", results=tmp_path / "results")
    assert counts_ == {"test/run1": 13}
    con = runlog.connect(tmp_path / "runs.db")
    assert sum(runlog.vector(con, "test/run1/cleaned/seed1/test")) == 1147
    row = con.execute("SELECT kind, split, shots FROM runs WHERE run_id = 'test/run1/base/qwen3-4b/4shot/test'").fetchone()
    assert tuple(row) == ("base", "test", 4)
