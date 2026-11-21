"""Hand tags for the failures the rules left as `other`: a random sample of 50 test items (decision 53).

errortags.py tags every wrong prediction by rule (decision 48). The last tag, `other`, is "anything
else", so the rules say nothing about why those predictions failed. This module draws a sample of the
items behind them and writes a sheet for Prit to tag by hand, then checks the filled sheet and counts it.

Population: the distinct test items on which at least one of the 10 adapters (5 cleaned, 5 random seeds)
has a failure the rules tagged `other` in the recorded test run (results/test/run1). The base-model passes
are not in it. The draw is `random.Random(20261120).sample` of the ids in sorted order, 50 of them, then
sorted by id. The row shows one prediction per item: the adapter pass is chosen at random (same generator,
continued, in sheet order) among the adapters whose prediction on that item was tagged `other`. The sheet
therefore describes items, not failures, and one prediction per item. The share of a tag is a share of
items in the pool.

Each sheet row is tagged with one of TAGS, the first that holds (the vocabulary was fixed on 21 Nov 2026,
from the dev failures tagged `other`, before any test prediction was looked at):

  gold_wrong       the gold program is wrong, the question is ambiguous or unanswerable, or the prediction
                   would be right under the correct label; a wrong gold program makes the item unanswerable
                   as scored, because a correct prediction would also fail against it (the note says what
                   is right). When only the written answer is wrong and the gold program is right, the
                   failure is the model's: tag its own reason and say in the note that the written answer
                   is also wrong
  invented_number  the program uses a number that is nowhere in the report and is not a constant
  wrong_quantity   the numbers come from the report, but the program computes another quantity than the
                   question asks: another entity, year or measure, a wrong base or denominator, or a stated
                   figure for something else used as if it answered the question
  missing_step     the right quantity, but a needed step or term is absent: no scale step, no change step,
                   years or items left out of a sum or an average
  extra_step       the right quantity, plus steps the question does not need
  wrong_constant   the right structure, but a wrong `const_*`, divisor or scale
  unclear          none of the above, or the reason cannot be told

`note` is one line: what the prediction does, and the right calculation with its numbers.

The sheet and the counts never change what the rules decided; they add the reasons.

  handcheck/tag_other.csv  one row per item, `tag` and `note` empty (UTF-8 with BOM, like the check sheets)
  handcheck/tag_other.md   the context for reading: question, gold, shown prediction, table, text

An existing .csv is never overwritten, because it may hold tags.

Usage: python -m finqa_lora.othertags             build the sheet and the reading file
       python -m finqa_lora.othertags --validate  check a filled sheet (exit 1 when a value is invalid)
       python -m finqa_lora.othertags --counts    count a finished sheet, write results/errors/other_tags.json
"""
import argparse
import collections
import csv
import json
import random
import sys
from pathlib import Path

from finqa_lora import REPO_ROOT, stats
from finqa_lora.data import load_split
from finqa_lora.errortags import TEST_RUN, tag_rows
from finqa_lora.handcheck import _item_numbers, _numbers, screen_status, table_md
from finqa_lora.screen import compare

SEED = 20261120
N = 50
NAME = "tag_other"
OUT = REPO_ROOT / "handcheck"
COUNTS = REPO_ROOT / "results" / "errors" / "other_tags.json"
TAGS = ("gold_wrong", "invented_number", "wrong_quantity", "missing_step", "extra_step", "wrong_constant",
        "unclear")
VERDICT_COLUMNS = ["tag", "note"]
SHEET_COLUMNS = ["item", "id", "split", "screen_status", "checked", "question", "answer", "exe_ans", "program",
                 "shown_pass", "other_passes", "pred_program", "pred_value"] + VERDICT_COLUMNS
CHECKED_SHEETS = ("check2", "check3")


def checked_column(root=REPO_ROOT):
    """{id: 'check2:real_error:program'} from the committed check sheets: what Prit decided about the gold
    label of each item they cover (an uncertain row gets ':uncertain')."""
    out = {}
    for check in CHECKED_SHEETS:
        with open(root / "handcheck" / f"{check}.csv", encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                parts = [check, r["verdict"]] + ([r["wrong_side"]] if r["wrong_side"] else []) \
                    + (["uncertain"] if r["uncertain"] else [])
                out[r["id"]] = ":".join(parts)
    return out


def adapter_other_failures(run=TEST_RUN):
    """{id: [(pass name, row), ...]} for every adapter failure the rules tagged `other`, in pass order."""
    from finqa_lora.testeval import load_run
    from finqa_lora.testpass import all_passes
    _, rows = load_run(run, load_split("test"))
    out = collections.defaultdict(list)
    for name in all_passes():
        if not name.startswith("adapter:"):
            continue
        by_id = {r["id"]: r for r in rows[name]}
        for t in tag_rows(rows[name], "test"):
            if t["tag"] == "other":
                out[t["id"]].append((name, by_id[t["id"]]))
    return out


def draw(run=TEST_RUN):
    """(sample, pool): sample = [(item, shown pass, its row, all `other` passes of the item)] in sheet order;
    pool = the sorted ids of the population."""
    failures = adapter_other_failures(run)
    pool = sorted(failures)
    rng = random.Random(SEED)
    ids = sorted(rng.sample(pool, N))
    items = {ex["id"]: ex for ex in load_split("test")}
    sample = []
    for id_ in ids:
        passes = failures[id_]
        name, row = rng.choice(passes)
        sample.append((items[id_], name, row, [n for n, _ in passes]))
    return sample, pool


def sheet_rows(sample, status, checked):
    """The read-only columns of every sheet row, as the sheet holds them (every value a string)."""
    rows = []
    for i, (ex, name, row, passes) in enumerate(sample, 1):
        qa = ex["qa"]
        rows.append({"item": str(i), "id": ex["id"], "split": "test", "screen_status": status[ex["id"]],
                     "checked": checked.get(ex["id"], ""), "question": qa["question"],
                     "answer": str(qa["answer"]).strip(), "exe_ans": str(qa["exe_ans"]),
                     "program": qa["program"], "shown_pass": name,
                     "other_passes": f"{len(passes)} of 10", "pred_program": row["program"],
                     "pred_value": row["value"]})
    return rows


def item_md(n, ex, name, row, passes, status, checked):
    qa = ex["qa"]
    facts = "\n".join(f"- `{k}` {v}" for k, v in qa.get("gold_inds", {}).items()) or "(none)"
    written = str(qa["answer"]).strip()
    try:
        matches = bool(written) and compare(float(row["value"]), written) == "agree"
    except ValueError:
        matches = False
    return f"""## {n}. `{ex['id']}`  (screen: {status}; gold label hand-checked: {checked or 'no'})

**Question:** {qa['question']}

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `{written}` | `{qa['exe_ans']}` | `{qa['program']}` |

**Shown prediction** (`{name}`; the rules tagged an adapter failure `other` on this item for {len(passes)} of 10 adapters)

| Predicted program | Predicted value | Matches the written answer by the screen's rule |
| --- | --- | --- |
| `{row['program']}` | `{row['value']}` | {'yes' if matches else 'no'} |

**Gold facts**
{facts}

**Table**

{table_md(ex['table'])}

<details><summary>Text before the table</summary>

{' '.join(ex.get('pre_text', []))}
</details>

<details><summary>Text after the table</summary>

{' '.join(ex.get('post_text', []))}
</details>
"""


def build():
    csv_path = OUT / f"{NAME}.csv"
    if csv_path.exists():
        sys.exit(f"{csv_path} exists and may hold tags. Not overwriting.")
    sample, pool = draw()
    status, checked = screen_status("test"), checked_column()
    rows = sheet_rows(sample, status, checked)
    OUT.mkdir(exist_ok=True)
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(SHEET_COLUMNS)
        for r in rows:
            w.writerow([r[k] for k in SHEET_COLUMNS if k not in VERDICT_COLUMNS] + [""] * len(VERDICT_COLUMNS))
    with open(OUT / f"{NAME}.md", "w", encoding="utf-8") as f:
        f.write(f"# {NAME}: test items with an adapter failure tagged `other`, {len(sample)} of {len(pool)} items, "
                f"seed {SEED}\n\n")
        f.write("\n".join(item_md(i, ex, name, row, passes, status[ex["id"]], checked.get(ex["id"], ""))
                          for i, (ex, name, row, passes) in enumerate(sample, 1)))
    print(f"{NAME}: wrote {len(sample)} items (pool {len(pool)}) to {csv_path.name} and {NAME}.md")


def check_row(row, expected, ex):
    """(invalid, to_review) messages for one sheet row. expected: the read-only values of the row."""
    invalid, review = [], []
    for k, want in expected.items():
        got = row.get(k)
        if got is None or got != want:
            invalid.append(f"read-only column {k} changed: sheet {got!r}, expected {want!r} "
                           "(saved by a spreadsheet? restore it with git restore)")
    tag, note = (row.get("tag") or "").strip(), (row.get("note") or "").strip()
    if not tag:
        if note:
            invalid.append("note filled but tag empty")
        return invalid, review
    if tag not in TAGS:
        invalid.append(f"tag {tag!r} not in {TAGS}")
    if not note:
        invalid.append("note is empty")
    elif not (_numbers(note) & (_item_numbers(ex) | _numbers(expected["pred_program"])
                                | _numbers(expected["pred_value"]))):
        review.append("note has no number from its own item: written for another row?")
    return invalid, review


def validate(path=None):
    path = path or OUT / f"{NAME}.csv"
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    sample, pool = draw()
    status, checked = screen_status("test"), checked_column()
    expected = sheet_rows(sample, status, checked)
    report = {"rows": len(rows), "with_tag": 0, "invalid": [], "to_review": [], "pool": len(pool)}
    if rows and list(rows[0]) != SHEET_COLUMNS:
        report["invalid"].append(("-", "-", f"header changed: expected {SHEET_COLUMNS}"))
    if [r.get("id") for r in rows] != [e["id"] for e in expected]:
        report["invalid"].append(("-", "-", f"the rows are not the {N} items of the draw, in order"))
        return report
    for row, want, (ex, *_rest) in zip(rows, expected, sample):
        bad, look = check_row(row, want, ex)
        report["with_tag"] += bool((row.get("tag") or "").strip())
        report["invalid"] += [(row["item"], row["id"], m) for m in bad]
        report["to_review"] += [(row["item"], row["id"], m) for m in look]
    return report


def counts(path=None, pool_size=None):
    """Counts of a finished sheet: per tag the items, the share of the sample with a 95% Wilson interval,
    and the same share scaled to the pool. None while the sheet is unfinished or invalid."""
    report = validate(path)
    if report["invalid"] or report["with_tag"] != N:
        return None, report
    with open(path or OUT / f"{NAME}.csv", encoding="utf-8-sig", newline="") as f:
        tags = collections.Counter(r["tag"].strip() for r in csv.DictReader(f))
    pool = pool_size or report["pool"]
    out = {"sample": N, "pool": pool, "seed": SEED, "tags": {}}
    for t in TAGS:
        k = tags[t]
        lo, hi = stats.wilson(k, N)
        out["tags"][t] = {"items": k, "share": k / N, "wilson_low": lo, "wilson_high": hi,
                          "pool_estimate": round(k / N * pool), "pool_low": round(lo * pool),
                          "pool_high": round(hi * pool)}
    return out, report


def print_report(r):
    print(f"{NAME}: {r['rows']} rows, {r['with_tag']} with a tag, {r['rows'] - r['with_tag']} to do (pool {r['pool']})")
    for title, key in (("Invalid (fix before committing)", "invalid"), ("To review (may be right)", "to_review")):
        print(f"{title}: {len(r[key])}")
        for item, id_, msg in r[key]:
            print(f"  item {item}  {id_}  {msg}")


def main():
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group()
    g.add_argument("--validate", action="store_true")
    g.add_argument("--counts", action="store_true")
    a = p.parse_args()
    if a.validate:
        r = validate()
        print_report(r)
        return 1 if r["invalid"] else 0
    if a.counts:
        out, r = counts()
        if out is None:
            print_report(r)
            print("not finished: counts need a valid tag on every row")
            return 1
        COUNTS.parent.mkdir(parents=True, exist_ok=True)
        with open(COUNTS, "w", encoding="utf-8", newline="\n") as f:
            json.dump(out, f, indent=2)
            f.write("\n")
        for t, v in out["tags"].items():
            print(f"{t:16s} {v['items']:3d}  {v['share']:.0%} ({v['wilson_low']:.0%}-{v['wilson_high']:.0%})")
        print(f"wrote {COUNTS.relative_to(REPO_ROOT).as_posix()}")
        return 0
    build()
    return 0


if __name__ == "__main__":
    sys.exit(main())
