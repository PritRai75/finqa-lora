"""Build hand-check sheets from the screen results, and check filled sheets. Prit fills every verdict.

  check1  50 random train flags (status disagree)            -> precision of the screen
  check2  every test item that is disagree, unparsed or no_answer -> confirmed test-set errors
  check3  50 random test items with status agree             -> what the screen misses

Each check writes two files to handcheck/:
  <check>.csv  one row per item, verdict columns empty (open in Excel; saved as UTF-8 with BOM)
  <check>.md   the full context for reading: question, answers, program, gold facts, table, text

An existing .csv is never overwritten, because it may hold verdicts.

--validate reads a filled sheet and lists problems: values outside the allowed lists, columns
filled or left empty against the protocol, corrected programs that do not run or do not give the
corrected answer, and notes with no number from their own item. It reports only; it never changes
a verdict. It also compares the item columns (question, answer, exe_ans, program, ...) on every
row with the data, because a spreadsheet save rewrites them (43.9% -> 43.90%, 0.0 -> 0). It exits
1 when a value is invalid, so it can run before every commit of verdicts.

Usage: python -m finqa_lora.handcheck check1
       python -m finqa_lora.handcheck check1 --validate
"""
import csv
import random
import re
import sys

from finqa_lora import REPO_ROOT
from finqa_lora.data import load_split
from finqa_lora.scoring import execute
from finqa_lora.screen import compare, parse_answer

SEED = 20261103
OUT = REPO_ROOT / "handcheck"
CHECKS = {
    "check1": ("train", ("disagree",), 50),
    "check2": ("test", ("disagree", "unparsed", "no_answer"), None),
    "check3": ("test", ("agree",), 50),
}
VERDICT_COLUMNS = ["verdict", "wrong_side", "error_type", "corrected_answer",
                   "corrected_program", "uncertain", "note"]

# Allowed values, fixed on 10 Nov 2026 before check1 (decision guide, decisions 1 to 5).
VERDICTS = ("real_error", "no_error", "parser_miss", "rounding", "sign_convention")
WRONG_SIDES = ("program", "answer", "both", "question_ambiguous")
ERROR_TYPES = ("wrong_number", "wrong_table_row", "wrong_operation", "operand_order", "step_count",
               "scale_or_units", "answer_typo", "missing_answer", "other")
ANSWER_ONLY_TYPES = ("answer_typo", "missing_answer")
UNCERTAIN = ("", "true")
SHEET_COLUMNS = ["item", "id", "split", "screen_status", "question", "answer", "exe_ans", "program"] + VERDICT_COLUMNS
_NUMBER = re.compile(r"\d[\d,]*(?:\.\d+)?|\.\d+")


def screen_status(split):
    path = REPO_ROOT / "results" / "screen" / f"{split}.csv"
    if not path.exists():
        sys.exit(f"{path} is missing. Run: python -m finqa_lora.screen")
    with open(path, encoding="utf-8") as f:
        return {r["id"]: r["status"] for r in csv.DictReader(f)}


def table_md(table):
    if not table:
        return "(no table)"
    width = max(len(r) for r in table)
    rows = [[str(c).replace("|", "/") for c in r] + [""] * (width - len(r)) for r in table]
    lines = ["| " + " | ".join(rows[0]) + " |", "|" + " --- |" * width]
    lines += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n".join(lines)


def item_md(n, ex, status):
    qa = ex["qa"]
    facts = "\n".join(f"- `{k}` {v}" for k, v in qa.get("gold_inds", {}).items()) or "(none)"
    return f"""## {n}. `{ex['id']}`  (screen: {status})

**Question:** {qa['question']}

| Written answer | Program result (exe_ans) | Gold program |
| --- | --- | --- |
| `{str(qa['answer']).strip()}` | `{qa['exe_ans']}` | `{qa['program']}` |

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


def build(check):
    split, statuses, n = CHECKS[check]
    status = screen_status(split)
    data = load_split(split)
    pool = [ex for ex in data if status[ex["id"]] in statuses]
    items = sorted(random.Random(SEED).sample(pool, n), key=lambda e: e["id"]) if n else pool
    OUT.mkdir(exist_ok=True)
    csv_path = OUT / f"{check}.csv"
    if csv_path.exists():
        sys.exit(f"{csv_path} exists and may hold verdicts. Not overwriting.")
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(SHEET_COLUMNS)
        for i, ex in enumerate(items, 1):
            qa = ex["qa"]
            w.writerow([i, ex["id"], split, status[ex["id"]], qa["question"], str(qa["answer"]).strip(),
                        qa["exe_ans"], qa["program"]] + [""] * len(VERDICT_COLUMNS))
    with open(OUT / f"{check}.md", "w", encoding="utf-8") as f:
        f.write(f"# {check}: {split}, status in {list(statuses)}, {len(items)} of {len(pool)} items, seed {SEED}\n\n")
        f.write("\n".join(item_md(i, ex, status[ex["id"]]) for i, ex in enumerate(items, 1)))
    print(f"{check}: wrote {len(items)} items (pool {len(pool)}) to {csv_path.name} and {check}.md")


def _numbers(text):
    out = set()
    for m in _NUMBER.findall(str(text)):
        try:
            out.add(round(float(m.replace(",", "")), 6))
        except ValueError:
            pass
    return out


def _item_numbers(ex):
    qa = ex["qa"]
    parts = [qa["question"], qa["answer"], qa["exe_ans"], qa["program"], " ".join(ex.get("pre_text", [])),
             " ".join(ex.get("post_text", []))] + [c for row in ex["table"] for c in row]
    return set().union(*(_numbers(p) for p in parts))


def read_only_values(ex, split, status):
    """The item columns exactly as build() writes them. A spreadsheet save often rewrites these."""
    qa = ex["qa"]
    return {"id": ex["id"], "split": split, "screen_status": status, "question": qa["question"],
            "answer": str(qa["answer"]).strip(), "exe_ans": str(qa["exe_ans"]), "program": qa["program"]}


def check_row(row, ex, split=None, status=None):
    """Return (invalid, to_review) lists of messages for one sheet row.

    Read-only columns are compared on every row. Verdict columns are checked only when a verdict
    is filled. split and status default to the row's own values (tests pass items directly).
    """
    invalid, review = [], []
    expected = read_only_values(ex, split or row.get("split"), status or row.get("screen_status"))
    for k, want in expected.items():
        got = row.get(k)
        if got is None or got != want:
            invalid.append(f"read-only column {k} changed: sheet {got!r}, item {want!r} "
                           "(saved by a spreadsheet? restore it with git restore)")
    v = {k: (row.get(k) or "").strip() for k in VERDICT_COLUMNS}
    if not v["verdict"]:
        if any(v[k] for k in VERDICT_COLUMNS):
            invalid.append("columns filled but verdict empty")
        return invalid, review
    if v["verdict"] not in VERDICTS:
        invalid.append(f"verdict {v['verdict']!r} not in {VERDICTS}")
    if v["uncertain"] not in UNCERTAIN:
        invalid.append(f"uncertain {v['uncertain']!r} must be empty or 'true'")
    if not v["note"]:
        invalid.append("note is empty")
    elif not (_numbers(v["note"]) & _item_numbers(ex)):
        review.append("note has no number from its own item: written for another row?")

    if v["verdict"] != "real_error":
        for k in ("wrong_side", "error_type", "corrected_answer", "corrected_program"):
            if v[k]:
                invalid.append(f"{k} must be empty unless verdict is real_error")
        return invalid, review

    side, etype = v["wrong_side"], v["error_type"]
    if side not in WRONG_SIDES:
        invalid.append(f"wrong_side {side!r} not in {WRONG_SIDES}")
    if side == "question_ambiguous":
        for k in ("error_type", "corrected_answer", "corrected_program"):
            if v[k]:
                invalid.append(f"{k} must be empty for question_ambiguous")
        return invalid, review
    if etype not in ERROR_TYPES:
        invalid.append(f"error_type {etype!r} not in {ERROR_TYPES}")
    if etype in ANSWER_ONLY_TYPES and side not in ("answer", "both"):
        invalid.append(f"error_type {etype} needs wrong_side answer or both")
    if etype == "missing_answer" and str(ex["qa"]["answer"]).strip():
        invalid.append("missing_answer, but the item has a written answer")
    if not str(ex["qa"]["answer"]).strip() and etype != "missing_answer" and side != "both":
        review.append("empty written answer: decision 2 codes it missing_answer (or both, if the program is also wrong)")

    if not v["corrected_answer"]:
        invalid.append("corrected_answer is empty")
        return invalid, review
    value, _ = parse_answer(v["corrected_answer"])
    if value is None:
        invalid.append(f"corrected_answer {v['corrected_answer']!r} cannot be read as a number or yes/no")
        return invalid, review

    if side in ("program", "both"):
        if not v["corrected_program"]:
            invalid.append("corrected_program is empty, but the program is wrong")
            return invalid, review
        ok, result = execute(v["corrected_program"], ex["table"])
        if not ok:
            invalid.append("corrected_program does not run")
        elif compare(result, v["corrected_answer"]) != "agree":
            review.append(f"corrected_program gives {result}, which does not match corrected_answer")
        if side == "program" and str(ex["qa"]["answer"]).strip() \
                and compare(value, ex["qa"]["answer"]) != "agree":
            review.append("wrong_side is program, but corrected_answer differs from the written answer")
    else:
        if v["corrected_program"]:
            invalid.append("corrected_program must be empty when only the answer is wrong")
        if compare(ex["qa"]["exe_ans"], v["corrected_answer"]) != "agree":
            review.append("wrong_side is answer, but corrected_answer differs from the program result")
    return invalid, review


def validate(check):
    split = CHECKS[check][0]
    path = OUT / f"{check}.csv"
    with open(path, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    items = {ex["id"]: ex for ex in load_split(split)}
    status = screen_status(split)
    report = {"rows": len(rows), "with_verdict": 0, "invalid": [], "to_review": []}
    if rows and list(rows[0]) != SHEET_COLUMNS:
        report["invalid"].append(("-", "-", f"header changed: expected {SHEET_COLUMNS}"))
    for row in rows:
        ex = items.get(row.get("id"))
        if ex is None:
            report["invalid"].append((row.get("item"), row.get("id"), "id not in the split"))
            continue
        bad, look = check_row(row, ex, split, status[ex["id"]])
        report["with_verdict"] += bool((row.get("verdict") or "").strip())
        report["invalid"] += [(row["item"], row["id"], m) for m in bad]
        report["to_review"] += [(row["item"], row["id"], m) for m in look]
    return report


def print_report(check, r):
    print(f"{check}: {r['rows']} rows, {r['with_verdict']} with a verdict, {r['rows'] - r['with_verdict']} to do")
    for title, key in (("Invalid (fix before committing)", "invalid"), ("To review (may be right)", "to_review")):
        print(f"{title}: {len(r[key])}")
        for item, id_, msg in r[key]:
            print(f"  item {item}  {id_}  {msg}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] not in CHECKS or args[1:] not in ([], ["--validate"]):
        sys.exit(f"usage: python -m finqa_lora.handcheck {{{'|'.join(CHECKS)}}} [--validate]")
    if args[1:] == ["--validate"]:
        rep = validate(args[0])
        print_report(args[0], rep)
        sys.exit(1 if rep["invalid"] else 0)
    build(args[0])
