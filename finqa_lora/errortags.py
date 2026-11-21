"""Rule-based error tags for wrong model predictions: one primary tag per failure, where a rule decides.

Written in S7 (19 Nov 2026) on dev predictions only, before any test prediction exists, so the rules
are fixed before they are applied to test. Dev is not hand-checked, so looking at it is allowed.

A failure is an item with exe_correct 0. Its program is compared with the gold program, step by step
(official tokenizer; numbers read as the official executor reads them, so `5%` is 0.05 and `const_100`
is 100; add and multiply compare their two arguments in either order). The first rule that holds gives
the tag:

  invalid          empty, does not parse or does not run
  operand_order    same operations in the same order with the same set of numbers, placed differently
                   (subtract(a, b) for subtract(b, a); a change measured from the wrong year)
  scale_x100       the value is the gold value x 100 or / 100 (a percentage given in the other form)
  sign             the value is minus the gold value
  near_value       the value is within 0.01% of the gold value but not equal at 5 decimals
  wrong_operation  same steps with the same arguments, but some operation differs
  wrong_table_row  same operations and step references; a number differs, and some differing number
                   sits in the same table column as the gold number, in another body row (row 0, the
                   header, does not count), or a table_* operation names another row
  wrong_number     same operations and step references; only numbers differ
  step_count       one program is the other with steps added or missing at the end
  other            anything else: left for hand tagging (a different approach, usually)

"Value" comparisons use a relative tolerance of 1e-4 (absolute 1e-5) on numbers, and need a nonzero
gold value. Two facts are reported beside the tag, not instead of it: the item's screen status, and
whether the predicted value matches the item's written answer by the screen's own rule
(`screen.compare(value, answer) == "agree"`). The summary counts that match on flagged items only
(screen status not `agree`): there a failure that matches the written answer is a candidate label
error, not necessarily a model error (the averaging template on dev is the clearest case). On `agree`
items the screen's tolerance (any x100) would count scale_x100 failures as matches, so they are not
summed.

Test (added S8, 20 Nov 2026, before the test passes were recorded; rules, order and summary unchanged,
decision 48): the 13 passes of a recorded test run, read and checked as finqa_lora.testeval reads them
(no pass missing, one gate record, every test.csv covering the 1,147 items in split order). On test the
flagged items (screen status other than `agree`, as on dev) are 107: check2's 98 plus the 9 `sign_only`.

Usage: python -m finqa_lora.errortags dev    tags every committed dev prediction file, writes
                                             results/errors/dev.json and prints a Markdown table
       python -m finqa_lora.errortags test [--run results/test/run1]
                                             the same for every pass of a recorded test run, writes
                                             results/errors/test.json
"""
import argparse
import collections
import csv
import json
import math
import sys
from pathlib import Path

from finqa_lora import REPO_ROOT
from finqa_lora.data import load_split
from finqa_lora.handcheck import screen_status
from finqa_lora.scoring import official, tokenize
from finqa_lora.screen import compare

TAGS = ("invalid", "operand_order", "scale_x100", "sign", "near_value", "wrong_operation",
        "wrong_table_row", "wrong_number", "step_count", "other")
COMMUTATIVE = ("add", "multiply")
REL, ABS = 1e-4, 1e-5
OUT = REPO_ROOT / "results" / "errors"


def _arg(op, raw, pos):
    raw = raw.strip()
    if raw.startswith("#"):
        return raw
    if op.startswith("table"):
        return ("row", raw) if pos == 0 else raw
    value = official.str_to_num(raw)
    return ("bad", raw) if value == "n/a" else round(float(value), 6)


def steps(program):
    """[(op, arg1, arg2)] with numbers as floats and references as '#k'; None if it does not parse."""
    try:
        tokens = tokenize(program)[:-1]
    except Exception:
        return None
    if not tokens or len(tokens) % 4:
        return None
    out = []
    for i in range(0, len(tokens), 4):
        op, a, b, close = tokens[i].rstrip("(").strip(), tokens[i + 1], tokens[i + 2], tokens[i + 3]
        if close != ")" or not op:
            return None
        out.append((op, _arg(op, a, 0), _arg(op, b, 1)))
    return out


def _key(step):
    """A step with the arguments of add and multiply put in a fixed order."""
    op, a, b = step
    if op in COMMUTATIVE:
        a, b = sorted((a, b), key=repr)
    return op, a, b


def _is_ref(x):
    return isinstance(x, str) and x.startswith("#")


def _numbers(st):
    return {x for _, a, b in st for x in (a, b) if isinstance(x, float)}


def _close(x, y):
    return math.isclose(x, y, rel_tol=REL, abs_tol=ABS)


def _cells(table):
    """{value: {(row, column)}} for every numeric body cell (row 0 is the header), read as the official
    executor reads rows."""
    out = collections.defaultdict(set)
    for r, row in enumerate(table[1:], 1):
        for c, cell in enumerate(row[1:], 1):
            v = official.str_to_num(str(cell).replace("$", "").strip().split("(")[0].strip())
            if v != "n/a":
                out[round(float(v), 6)].add((r, c))
    return out


def _table_row_slip(pred, gold, table):
    cells = _cells(table)
    for p, g in zip(pred, gold):
        for x, y in zip(p[1:], g[1:]):
            if x == y:
                continue
            if isinstance(x, tuple) and isinstance(y, tuple) and x[0] == y[0] == "row":
                return True
            if isinstance(x, float) and isinstance(y, float):
                for (rx, cx) in cells.get(x, ()):
                    if any(cx == cy and rx != ry for ry, cy in cells.get(y, ())):
                        return True
    return False


def tag(program, executes, value, ex):
    """The primary tag of one wrong prediction. value: the stored value (string or number)."""
    if not str(program).strip() or not int(executes):
        return "invalid"
    pred, gold = steps(program), steps(ex["qa"]["program"])
    if pred is None or gold is None:
        return "invalid"
    p, g = [_key(s) for s in pred], [_key(s) for s in gold]
    same_ops = len(p) == len(g) and all(a[0] == b[0] for a, b in zip(p, g))
    if same_ops and p != g and _numbers(pred) and _numbers(pred) == _numbers(gold):
        return "operand_order"
    gv = ex["qa"]["exe_ans"]
    try:
        v = float(value)
    except (TypeError, ValueError):
        v = None
    if isinstance(gv, float) and v is not None and gv != 0:
        if _close(v, gv * 100) or _close(v, gv / 100):
            return "scale_x100"
        if _close(v, -gv):
            return "sign"
        if _close(v, gv):
            return "near_value"
    if len(p) == len(g) and all(sorted((a[1], a[2]), key=repr) == sorted((b[1], b[2]), key=repr)
                                for a, b in zip(p, g)):
        return "wrong_operation"
    if same_ops and all(_is_ref(x) == _is_ref(y) and (not _is_ref(x) or x == y)
                        for a, b in zip(p, g) for x, y in zip(a[1:], b[1:])):
        return "wrong_table_row" if _table_row_slip(p, g, ex["table"]) else "wrong_number"
    if len(p) != len(g) and (p == g[:len(p)] or g == p[:len(g)]):
        return "step_count"
    return "other"


def tag_rows(rows, split):
    """Tag every failure in a prediction file's rows. Returns [{id, tag, screen_status, matches_answer}]."""
    items = {ex["id"]: ex for ex in load_split(split)}
    status = screen_status(split)
    out = []
    for r in rows:
        if int(r["exe_correct"]):
            continue
        ex = items[r["id"]]
        t = tag(r["program"], r["executes"], r["value"], ex)
        answer = str(ex["qa"]["answer"]).strip()
        try:
            v = float(r["value"])
        except (TypeError, ValueError):
            v = r["value"] or None
        matches = bool(answer) and v is not None and t != "invalid" and compare(v, answer) == "agree"
        out.append({"id": r["id"], "tag": t, "screen_status": status[r["id"]], "matches_answer": matches})
    return out


def dev_files(root=REPO_ROOT):
    """{run name: dev prediction CSV} for the main runs and the prompted base models on dev."""
    files = {}
    for path in sorted((root / "results" / "main").glob("run*/*/seed*/dev.csv")):
        files[f"adapter:{path.parts[-3]}:{path.parts[-2].removeprefix('seed')}"] = path
    for path in sorted((root / "results" / "feasibility" / "run1").glob("*/dev_base_?shot.csv")):
        files[f"base:{path.parent.name}:{path.stem.removeprefix('dev_base_')}"] = path
    return files


def summarise(tagged):
    tags = collections.Counter(t["tag"] for t in tagged)
    flagged = [t for t in tagged if t["screen_status"] != "agree"]
    return {"failures": len(tagged), "tags": {k: tags[k] for k in TAGS},
            "on_flagged_items": len(flagged),
            "flagged_matching_written_answer": sum(t["matches_answer"] for t in flagged)}


def run_dev(root=REPO_ROOT, write=True):
    out = {}
    for name, path in dev_files(root).items():
        with open(path, encoding="utf-8", newline="") as f:
            out[name] = summarise(tag_rows(list(csv.DictReader(f)), "dev"))
    if write:
        OUT.mkdir(parents=True, exist_ok=True)
        with open(OUT / "dev.json", "w", encoding="utf-8", newline="\n") as f:
            json.dump(out, f, indent=2)
            f.write("\n")
    return out


TEST_RUN = REPO_ROOT / "results" / "test" / "run1"


def run_test(run=TEST_RUN, write=True):
    """{pass name: summary} for every pass of a recorded test run, in testpass.all_passes order."""
    from finqa_lora.testeval import load_run
    from finqa_lora.testpass import all_passes
    _, rows = load_run(run, load_split("test"))
    out = {name: summarise(tag_rows(rows[name], "test")) for name in all_passes()}
    if write:
        OUT.mkdir(parents=True, exist_ok=True)
        with open(OUT / "test.json", "w", encoding="utf-8", newline="\n") as f:
            json.dump(out, f, indent=2)
            f.write("\n")
    return out


def markdown(summary):
    head = ["Run", "Failures"] + list(TAGS) + ["On flagged items", "of which match the written answer"]
    lines = ["| " + " | ".join(head) + " |", "|" + " --- |" * len(head)]
    for name, s in summary.items():
        lines.append("| " + " | ".join([name, str(s["failures"])] + [str(s["tags"][t]) for t in TAGS]
                                        + [str(s["on_flagged_items"]), str(s["flagged_matching_written_answer"])]) + " |")
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("split", choices=["dev", "test"])
    p.add_argument("--run", default=str(TEST_RUN), help="test only: the recorded test run")
    a = p.parse_args()
    print(markdown(run_dev() if a.split == "dev" else run_test(Path(a.run))))
    print(f"\nwrote {(OUT / f'{a.split}.json').relative_to(REPO_ROOT).as_posix()}")


if __name__ == "__main__":
    sys.exit(main())
