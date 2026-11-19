"""Test results: the three test views and every statistic of the comparison, from a recorded test run.

Written and tested on made-up predictions before any test number existed (S6, 19 Nov 2026), so the
rules below are fixed before the results they govern. Input: results/test/run<k>/ as written by
jobs/testpass.sh, and the committed check2 and check3 sheets. Output: <run>/evaluation.json and a
Markdown summary on stdout.

Views (spec section 5; the item rules marked "S6" are this module's reading, decision 45):
  official    all 1,147 items, scored against exe_ans exactly as the test passes scored them.
  consistent  items with no known or possible label problem: screen `agree` items not found wrong
              by check3, plus check2 and check3 items whose verdict is not `real_error`. Leaves out
              every `real_error` (any side), every `uncertain` verdict and, S6, the 9 `sign_only`
              items, which no check covers.
  corrected   all items except `uncertain` and `question_ambiguous` ones, scored against the right
              value: for a `real_error` on the program side (`program` or `both`), S6, the result of
              running `corrected_program` (the validator has checked that it runs); for an
              answer-side error, exe_ans, which the gold program already gives. `sign_only` items
              keep exe_ans.
Every model is re-scored from its own program in every view; in the official view this must give
back the stored exe_correct of every item, or the module stops.

Statistics, per view:
  - every pass: count, accuracy and 95% Wilson interval
  - fine-tuned versus each prompted base (S6): exact McNemar of each of the 10 adapters against the
    base; "fine-tuning beats <base>" only if all 10 are better with p < 0.05, "<base> beats
    fine-tuning" only if all 10 are worse with p < 0.05, otherwise "mixed". Range of p reported.
  - cleaned versus random: stats.winner on the 5 + 5 adapters (decision 39).
The official view is the headline (spec, section 4).

The sheets used must be the ones the test passes were let through by: the git blob of each sheet
now must equal the blob in the test run's gate record, or the module stops.

Usage: python -m finqa_lora.testeval results/test/run1
"""
import argparse
import csv
import json
import sys
from pathlib import Path

from finqa_lora import REPO_ROOT, stats
from finqa_lora.data import load_split
from finqa_lora.handcheck import screen_status
from finqa_lora.mainruns import ARMS, SEEDS
from finqa_lora.scoring import execute
from finqa_lora.testpass import BASE_PASSES, all_passes

VIEWS = ("official", "consistent", "corrected")
NOT_ERRORS = ("no_error", "parser_miss", "rounding", "sign_convention")
ADAPTERS = [f"adapter:{a}:{s}" for a in ARMS for s in SEEDS]
BASES = [f"base:{m}:{k}" for m, k in BASE_PASSES]
P_LIMIT = 0.05


def read_sheet(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        return {r["id"]: r for r in csv.DictReader(f)}


def item_rules(items, status, sheets):
    """For each test item: in the consistent view? in the corrected view? and its corrected target.

    sheets: {check: {id: row}} for check2 and check3. Returns {id: {...}} in split order, plus counts.
    """
    verdict_of = {}
    for check, rows in sheets.items():
        for i, r in rows.items():
            if i in verdict_of:
                raise ValueError(f"{i} has a verdict in two sheets")
            verdict_of[i] = (check, r)
    rules, why = {}, {}
    for ex in items:
        i, st = ex["id"], status[ex["id"]]
        target = ex["qa"]["exe_ans"]
        if i in verdict_of:
            check, r = verdict_of[i]
            v, side = r["verdict"].strip(), r["wrong_side"].strip()
            if not v:
                raise ValueError(f"{check} has no verdict for {i}")
            if r["uncertain"].strip() == "true":
                rule = (False, False, "uncertain")
            elif v in NOT_ERRORS:
                rule = (True, True, f"{check}:{v}")
            elif v == "real_error" and side == "question_ambiguous":
                rule = (False, False, "question_ambiguous")
            elif v == "real_error" and side in ("program", "both"):
                ok, value = execute(r["corrected_program"].strip(), ex["table"])
                if not ok:
                    raise ValueError(f"{check} {i}: corrected_program does not run")
                target = value
                rule = (False, True, f"real_error:{side}")
            elif v == "real_error" and side == "answer":
                rule = (False, True, "real_error:answer")
            else:
                raise ValueError(f"{check} {i}: verdict {v!r} / wrong_side {side!r} not covered")
        elif st == "agree":
            rule = (True, True, "agree")
        elif st == "sign_only":
            rule = (False, True, "sign_only")
        else:
            raise ValueError(f"{i}: screen status {st} but no check2 verdict (check2 covers every one)")
        rules[i] = {"consistent": rule[0], "corrected": rule[1], "target": target, "reason": rule[2]}
        why[rule[2]] = why.get(rule[2], 0) + 1
    return rules, dict(sorted(why.items()))


def rescore(rows, by_id, rules):
    """Per-item 0/1 in each view, in split order, from each item's own program."""
    out = {v: [] for v in VIEWS}
    for r in rows:
        ex = by_id[r["id"]]
        program = r["program"]
        ok, value = execute(program, ex["table"]) if program else (False, None)
        official = int(ok and value == ex["qa"]["exe_ans"])
        if official != int(r["exe_correct"]):
            raise ValueError(f"{r['id']}: re-scored {official}, stored exe_correct {r['exe_correct']}")
        rule = rules[r["id"]]
        out["official"].append(official)
        if rule["consistent"]:
            out["consistent"].append(official)
        if rule["corrected"]:
            out["corrected"].append(int(ok and value == rule["target"]))
    return out


def load_run(run, items):
    """{pass name: rows in split order}. Every pass must cover every test item once."""
    run = Path(run)
    with open(run / "report.json", encoding="utf-8") as f:
        report = json.load(f)
    if report["missing_passes"]:
        raise SystemExit(f"{run}: missing passes {report['missing_passes']}")
    if not report.get("one_gate_record"):
        raise SystemExit(f"{run}: the passes were let through by different sheet versions")
    order = [ex["id"] for ex in items]
    found = {}
    for path in sorted(run.rglob("result.json")):
        if "devcheck" in path.parts:
            continue
        with open(path, encoding="utf-8") as f:
            res = json.load(f)
        with open(path.parent / "test.csv", encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        if [r["id"] for r in rows] != order:
            raise SystemExit(f"{path.parent}: test.csv does not cover the 1,147 test items in split order")
        if sum(int(r["exe_correct"]) for r in rows) != res["test"]["exe_correct"]:
            raise SystemExit(f"{path.parent}: test.csv and result.json disagree")
        found[res["pass"]] = rows
    if sorted(found) != sorted(all_passes()):
        raise SystemExit(f"{run}: passes found {sorted(found)}")
    return report, found


def sheets_match_gate(gate, root=REPO_ROOT):
    """The committed sheets now must be the ones that opened the gate for these passes."""
    from finqa_lora.testgate import TEST_CHECKS, _git
    for check in TEST_CHECKS:
        blob = _git("rev-parse", f"HEAD:handcheck/{check}.csv", root=root).stdout.strip()
        if blob != gate[check]["git_blob"]:
            raise SystemExit(f"handcheck/{check}.csv changed since the test passes ran "
                             f"(blob {blob[:12]} now, {gate[check]['git_blob'][:12]} at test time)")


def accuracy(v):
    k, n = sum(v), len(v)
    lo, hi = stats.wilson(k, n)
    return {"correct": k, "items": n, "accuracy": k / n, "wilson_low": lo, "wilson_high": hi}


def finetuned_vs_base(vectors):
    out = {}
    for base in BASES:
        tests = {a: stats.mcnemar_exact(vectors[a], vectors[base]) for a in ADAPTERS}
        better = [t["a_only"] > t["b_only"] and t["p"] < P_LIMIT for t in tests.values()]
        worse = [t["a_only"] < t["b_only"] and t["p"] < P_LIMIT for t in tests.values()]
        verdict = "fine-tuning beats the base" if all(better) else \
            "the base beats fine-tuning" if all(worse) else "mixed"
        out[base] = {"verdict": verdict, "p_max": max(t["p"] for t in tests.values()),
                     "p_min": min(t["p"] for t in tests.values()), "per_adapter": tests}
    return out


def evaluate(run, sheets=None, check_gate=True):
    items = load_split("test")
    by_id = {ex["id"]: ex for ex in items}
    report, found = load_run(run, items)
    if check_gate:
        sheets_match_gate(report["test_gate"])
    if sheets is None:
        sheets = {c: read_sheet(REPO_ROOT / "handcheck" / f"{c}.csv") for c in ("check2", "check3")}
    rules, reasons = item_rules(items, screen_status("test"), sheets)
    vectors = {v: {} for v in VIEWS}
    for name, rows in found.items():
        for view, vec in rescore(rows, by_id, rules).items():
            vectors[view][name] = vec
    out = {"run": Path(run).as_posix(), "item_reasons": reasons,
           "items": {v: len(next(iter(vectors[v].values()))) for v in VIEWS}, "views": {}}
    for view in VIEWS:
        vec = vectors[view]
        arms = {a: [vec[f"adapter:{a}:{s}"] for s in SEEDS] for a in ARMS}
        out["views"][view] = {
            "accuracy": {n: accuracy(v) for n, v in sorted(vec.items())},
            "arm_mean": {a: sum(map(sum, arms[a])) / (len(SEEDS) * len(arms[a][0])) for a in ARMS},
            "finetuned_vs_base": finetuned_vs_base(vec),
            "cleaned_vs_random": stats.winner(arms["cleaned"], arms["random"]),
        }
    with open(Path(run) / "evaluation.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    return out


def markdown(ev):
    lines = []
    for view in VIEWS:
        v = ev["views"][view]
        n = ev["items"][view]
        lines += [f"### {view} view ({n} items)", "", "| Model | Correct | Accuracy (95% Wilson) |", "| --- | --- | --- |"]
        for name, a in v["accuracy"].items():
            lines.append(f"| {name} | {a['correct']}/{a['items']} | {a['accuracy']:.1%} "
                         f"({a['wilson_low']:.1%}–{a['wilson_high']:.1%}) |")
        w = v["cleaned_vs_random"]
        lines += ["", f"Cleaned versus random: {w['verdict']}; difference {w['difference'] * 100:+.2f} pt, "
                      f"95% interval {w['low'] * 100:+.2f} to {w['high'] * 100:+.2f} pt; seed pairs "
                      + ", ".join(f"{d * 100:+.2f}" for d in w["seed_pair_differences"]) + "."]
        for base, r in v["finetuned_vs_base"].items():
            lines.append(f"Fine-tuned versus {base}: {r['verdict']} (McNemar p {r['p_min']:.2g} to {r['p_max']:.2g}).")
        lines.append("")
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("run", help="a recorded test run, e.g. results/test/run1")
    a = p.parse_args()
    ev = evaluate(a.run)
    print("items by rule:", ev["item_reasons"])
    print(markdown(ev))


if __name__ == "__main__":
    sys.exit(main())
