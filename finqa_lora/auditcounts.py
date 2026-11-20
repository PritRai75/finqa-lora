"""Audit counts from the hand-check sheets: what the screen's flags are, and what it misses.

Written and tested on made-up verdicts before any sheet had a verdict (S7, 19 Nov 2026), so every
definition below is fixed before the counts it governs. Verdicts are Prit's; this module only counts.

Only finished, valid sheets are counted: every row has a verdict, `handcheck --validate` finds nothing
invalid, and the sheet holds exactly the items it was built with. A sheet still being filled is
reported as in progress (rows done, rows to do) and nothing else is read from it.

Definitions. n = rows with a verdict that are not `uncertain`. Uncertain rows are left out of every
count (handcheck/README.md) and reported by number. For a real_error row:
  wrong_program        wrong_side program or both: the gold program is wrong (bad training data)
  wrong_written_answer wrong_side answer with any type but missing_answer, or both with a written answer
  missing_answer       wrong_side answer with type missing_answer (an empty answer, or text the screen
                       could not read that gives no value: decision 51), or both with an empty answer
                       (under both the type describes the program: decision 49). Counted apart from
                       wrong answers (decision 28)
  ambiguous            wrong_side question_ambiguous
A real_error is any of these, question_ambiguous included, as the README defines the verdict.

check1  (50 random train `disagree` items out of 431, seed 20261103)
  Share of n for every verdict and for the four kinds above, each with a 95% Wilson interval and
  scaled to the 431 flags (share x 431, interval x 431). Precision of the screen = real_error / n.
  The sample is drawn without replacement from 431; Wilson leaves out the finite-population
  correction, so the interval is a little wide. Parser misses are listed with their notes, as
  patterns of the screen's known limit: parser v1 is kept whatever they show (decision 47).
check2  (every test item that is `disagree`, `unparsed` or `no_answer`: 98, a census)
  Counts by screen status and verdict, real errors by kind, side and type. Precision of the screen
  on test `disagree` items with a Wilson interval (as a property of the screen; for the test set
  itself the count is exact).
check3  (50 random test `agree` items out of 1,040)
  Misses = real_error / n, with the exact one-sided 95% upper bound (Clopper-Pearson) on the miss
  rate and that bound x 1,040. 0 of 50 gives 5.8%.
Test set as a whole: real errors confirmed by check2 and check3 (a lower bound), and the estimate
check2 + check3 rate x 1,040 with its upper bound. The 9 `sign_only` test items are in no check and
are left out, which the output says.
Averaging template: gold programs whose last two steps are add(#k, const_3), divide(#k+1, const_2),
so they add 3 and halve instead of dividing by 3 (train 34, dev 8, test 2), with their screen status
and any verdicts they got.
Self-agreement (`agreement`): of the items re-checked blind, how many keep the same verdict, with a
Wilson interval and Cohen's kappa, on the five verdicts and on real_error versus not. Rows uncertain
in either pass are left out.

Usage: python -m finqa_lora.auditcounts          writes results/audit/counts.json, prints Markdown
"""
import collections
import csv
import json
import math
import re
import sys

from finqa_lora import REPO_ROOT, stats
from finqa_lora.data import load_split
from finqa_lora.handcheck import CHECKS, OUT, VERDICTS, screen_status, select_items, validate

KINDS = ("wrong_program", "wrong_written_answer", "missing_answer", "ambiguous")
ONE_SIDED = 0.05
AVERAGING = re.compile(r"add\(#(\d+), const_3\), divide\(#(\d+), const_2\)$")
OUT_FILE = REPO_ROOT / "results" / "audit" / "counts.json"


def kinds(row):
    """The kinds a real_error row counts towards (a row can be both wrong program and missing answer).

    Under `both` the error type describes the program (decision 49), so a missing answer is read from
    the written answer itself: empty means missing. Under `answer` it is the error type, which may
    also mark text the screen could not read and that gives no value (decision 51)."""
    side, etype = row["wrong_side"].strip(), row["error_type"].strip()
    out = set()
    if side == "question_ambiguous":
        out.add("ambiguous")
    if side in ("program", "both"):
        out.add("wrong_program")
    if side == "answer":
        out.add("missing_answer" if etype == "missing_answer" else "wrong_written_answer")
    if side == "both":
        out.add("wrong_written_answer" if row["answer"].strip() else "missing_answer")
    return out


def share(k, n, pool=None):
    if n == 0:
        return {"count": k, "of": 0}
    lo, hi = stats.wilson(k, n)
    out = {"count": k, "of": n, "share": k / n, "wilson_low": lo, "wilson_high": hi}
    if pool:
        out.update(pool=pool, in_pool=k / n * pool, in_pool_low=lo * pool, in_pool_high=hi * pool)
    return out


def upper_bound(k, n, alpha=ONE_SIDED):
    """Exact one-sided (1 - alpha) upper bound on a binomial rate: the p with P(X <= k | n, p) = alpha."""
    if not 0 <= k <= n or n <= 0:
        raise ValueError("need 0 <= k <= n and n > 0")
    if k == n:
        return 1.0
    if k == 0:
        return 1 - alpha ** (1 / n)

    def cdf(p):
        return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))
    lo, hi = k / n, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if cdf(mid) > alpha else (lo, mid)
    return (lo + hi) / 2


def read_rows(check, path=None):
    """(state, rows). state: missing, invalid, not started, in progress or complete."""
    path = path or OUT / f"{check}.csv"
    if not path.exists():
        return {"state": "missing"}, []
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    rep = validate(check, path)
    built = sorted(ex["id"] for ex in select_items(check)[0])
    state = {"rows": rep["rows"], "with_verdict": rep["with_verdict"], "invalid": len(rep["invalid"])}
    if rep["invalid"] or sorted(r["id"] for r in rows) != built:
        state["state"] = "invalid"
    elif rep["with_verdict"] == 0:
        state["state"] = "not started"
    elif rep["with_verdict"] < rep["rows"]:
        state["state"] = "in progress"
    else:
        state["state"] = "complete"
    return state, rows


def tally(rows, pool=None):
    """Counts for one finished sheet."""
    kept = [r for r in rows if r["uncertain"].strip() != "true"]
    n = len(kept)
    verdicts = collections.Counter(r["verdict"].strip() for r in kept)
    real = [r for r in kept if r["verdict"].strip() == "real_error"]
    kind_count = collections.Counter(k for r in real for k in kinds(r))
    return {
        "rows": len(rows), "uncertain": len(rows) - n, "counted": n,
        "verdicts": {v: share(verdicts[v], n, pool) for v in VERDICTS},
        "kinds": {k: share(kind_count[k], n, pool) for k in KINDS},
        "precision": share(verdicts["real_error"], n, pool),
        "wrong_side": dict(sorted(collections.Counter(r["wrong_side"].strip() for r in real).items())),
        "error_type": dict(sorted(collections.Counter(
            r["error_type"].strip() for r in real if r["wrong_side"].strip() != "question_ambiguous").items())),
        "side_by_type": dict(sorted(collections.Counter(
            f"{r['wrong_side'].strip()}/{r['error_type'].strip() or '-'}" for r in real).items())),
    }


def count_check1(rows):
    pool = sum(s == "disagree" for s in screen_status("train").values())
    out = tally(rows, pool)
    out["pool"] = pool
    out["parser_misses"] = [{"id": r["id"], "answer": r["answer"], "note": r["note"].strip()}
                            for r in rows if r["verdict"].strip() == "parser_miss" and r["uncertain"].strip() != "true"]
    return out


def count_check2(rows):
    out = tally(rows)
    by_status = collections.defaultdict(list)
    for r in rows:
        by_status[r["screen_status"]].append(r)
    out["by_status"] = {s: tally(rs) for s, rs in sorted(by_status.items())}
    if "disagree" in by_status:
        out["precision_disagree"] = out["by_status"]["disagree"]["precision"]
    return out


def count_check3(rows):
    pool = sum(s == "agree" for s in screen_status("test").values())
    out = tally(rows, pool)
    k, n = out["verdicts"]["real_error"]["count"], out["counted"]
    if n:
        ub = upper_bound(k, n)
        out["misses"] = {"count": k, "of": n, "rate": k / n, "upper95_one_sided": ub,
                         "pool": pool, "in_pool": k / n * pool, "in_pool_upper": ub * pool}
    out["pool"] = pool
    return out


def test_set_total(c2, c3):
    """Label problems on the 1,147 test items: confirmed, estimated and upper bound."""
    confirmed2 = c2["verdicts"]["real_error"]["count"]
    m = c3["misses"]
    return {"confirmed": confirmed2 + m["count"],
            "estimate": confirmed2 + m["in_pool"],
            "upper95": confirmed2 + m["in_pool_upper"],
            "not_covered": {"sign_only": sum(s == "sign_only" for s in screen_status("test").values()),
                            "uncertain": c2["uncertain"] + c3["uncertain"]},
            "note": "confirmed = real_error in check2 + check3; estimate and upper95 scale the check3 miss "
                    "rate to every test agree item; sign_only and uncertain items are in no count"}


def is_averaging(program):
    """Last two steps add const_3 to the previous step, then halve that sum."""
    m = AVERAGING.search(program.strip())
    return bool(m) and int(m.group(2)) == int(m.group(1)) + 1


def averaging_template(sheets=None):
    """Programs that add 3 and halve instead of dividing by 3, by split and screen status."""
    out = {}
    verdict_of = {}
    for check, rows in (sheets or {}).items():
        for r in rows:
            if r["verdict"].strip():
                verdict_of[r["id"]] = f"{check}:{r['verdict'].strip()}" + (
                    f":{r['wrong_side'].strip()}" if r["verdict"].strip() == "real_error" else "")
    for split in ("train", "dev", "test"):
        status = screen_status(split)
        ids = [ex["id"] for ex in load_split(split) if is_averaging(ex["qa"]["program"])]
        out[split] = {"items": len(ids),
                      "status": dict(sorted(collections.Counter(status[i] for i in ids).items())),
                      "verdicts": dict(sorted(collections.Counter(verdict_of[i] for i in ids if i in verdict_of).items()))}
    return out


def _kappa(pairs):
    n = len(pairs)
    observed = sum(a == b for a, b in pairs) / n
    first, second = collections.Counter(a for a, _ in pairs), collections.Counter(b for _, b in pairs)
    expected = sum(first[c] * second[c] for c in set(first) | set(second)) / (n * n)
    return 1.0 if expected == 1 else (observed - expected) / (1 - expected)


def agreement(first, second):
    """Self-agreement between two passes over the same items. first, second: {id: row}."""
    ids = [i for i in second if i in first and "true" not in
           (first[i]["uncertain"].strip(), second[i]["uncertain"].strip())]
    if not ids:
        raise ValueError("no item in both passes")
    out = {"items": len(ids), "left_out_uncertain": len([i for i in second if i in first]) - len(ids)}
    for name, key in (("verdict", lambda r: r["verdict"].strip()),
                      ("real_error", lambda r: r["verdict"].strip() == "real_error")):
        pairs = [(key(first[i]), key(second[i])) for i in ids]
        same = sum(a == b for a, b in pairs)
        out[name] = {**share(same, len(ids)), "kappa": _kappa(pairs)}
    return out


def count_all(paths=None):
    paths = paths or {}
    out, rows = {"sheets": {}}, {}
    for check in CHECKS:
        state, r = read_rows(check, paths.get(check))
        out["sheets"][check] = state
        if state["state"] == "complete":
            rows[check] = r
    counters = {"check1": count_check1, "check2": count_check2, "check3": count_check3}
    for check, r in rows.items():
        out[check] = counters[check](r)
    if "check2" in out and "check3" in out:
        out["test_set"] = test_set_total(out["check2"], out["check3"])
    out["averaging_template"] = averaging_template(rows)
    return out


def _pct(s):
    if not s.get("of"):
        return "–"
    return f"{s['count']}/{s['of']} = {s['share']:.0%} ({s['wilson_low']:.0%}–{s['wilson_high']:.0%})"


def markdown(c):
    lines = ["| Sheet | State | Rows with a verdict |", "| --- | --- | --- |"]
    for check, s in c["sheets"].items():
        lines.append(f"| {check} | {s['state']} | {s.get('with_verdict', 0)}/{s.get('rows', 0)} |")
    if "check1" in c:
        k = c["check1"]
        lines += ["", f"### check1: {k['counted']} train flags counted of {k['rows']} ({k['uncertain']} uncertain), pool {k['pool']}",
                  "", "| | Share (95% Wilson) | In the 431 flags |", "| --- | --- | --- |"]
        for name, s in [("precision (real_error)", k["precision"])] + list(k["kinds"].items()) + \
                [(v, k["verdicts"][v]) for v in VERDICTS if v != "real_error"]:
            pool = f"{s['in_pool']:.0f} ({s['in_pool_low']:.0f}–{s['in_pool_high']:.0f})" if s.get("of") else "–"
            lines.append(f"| {name} | {_pct(s)} | {pool} |")
        for p in k["parser_misses"]:
            lines.append(f"- parser miss `{p['id']}` (answer `{p['answer']}`): {p['note']}")
    if "check2" in c:
        k = c["check2"]
        lines += ["", f"### check2: {k['counted']} flagged test items counted of {k['rows']} ({k['uncertain']} uncertain)",
                  "", "| Screen status | Items | real_error | wrong program | wrong answer | missing answer | ambiguous |",
                  "| --- | --- | --- | --- | --- | --- | --- |"]
        for s, t in list(k["by_status"].items()) + [("all", k)]:
            lines.append(f"| {s} | {t['counted']} | {t['verdicts']['real_error']['count']} | "
                         + " | ".join(str(t["kinds"][x]["count"]) for x in KINDS) + " |")
        if "precision_disagree" in k:
            lines.append(f"\nScreen precision on test `disagree`: {_pct(k['precision_disagree'])}. Error types: {k['error_type']}")
    if "check3" in c:
        m = c["check3"].get("misses")
        if m:
            lines += ["", f"### check3: {m['count']} of {m['of']} test `agree` items are real errors; "
                          f"one-sided 95% upper bound {m['upper95_one_sided']:.1%}, at most {m['in_pool_upper']:.0f} of {m['pool']}"]
    if "test_set" in c:
        t = c["test_set"]
        lines.append(f"\nTest set: {t['confirmed']} label problems confirmed; estimate {t['estimate']:.1f}, "
                     f"upper bound {t['upper95']:.1f} of 1,147 (not covered: {t['not_covered']}).")
    a = c["averaging_template"]
    lines.append("\nAveraging template (adds 3 and halves): " + "; ".join(
        f"{s} {v['items']} {v['status']}" + (f" verdicts {v['verdicts']}" if v["verdicts"] else "") for s, v in a.items()))
    return "\n".join(lines)


def main():
    c = count_all()
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_FILE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(c, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(markdown(c))
    print(f"\nwrote {OUT_FILE.relative_to(REPO_ROOT).as_posix()}")


if __name__ == "__main__":
    sys.exit(main())
