"""Build hand-check sheets from the screen results. Claude builds the sheets; Prit fills every verdict.

  check1  50 random train flags (status disagree)            -> precision of the screen
  check2  every test item that is disagree, unparsed or no_answer -> confirmed test-set errors
  check3  50 random test items with status agree             -> what the screen misses

Each check writes two files to handcheck/:
  <check>.csv  one row per item, verdict columns empty (open in Excel; saved as UTF-8 with BOM)
  <check>.md   the full context for reading: question, answers, program, gold facts, table, text

An existing .csv is never overwritten, because it may hold verdicts.
Usage: python -m finqa_lora.handcheck check1
"""
import csv
import random
import sys

from finqa_lora import REPO_ROOT
from finqa_lora.data import load_split

SEED = 20261103
OUT = REPO_ROOT / "handcheck"
CHECKS = {
    "check1": ("train", ("disagree",), 50),
    "check2": ("test", ("disagree", "unparsed", "no_answer"), None),
    "check3": ("test", ("agree",), 50),
}
VERDICT_COLUMNS = ["verdict", "wrong_side", "error_type", "corrected_answer",
                   "corrected_program", "uncertain", "note"]


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
        w.writerow(["item", "id", "split", "screen_status", "question", "answer", "exe_ans", "program"]
                   + VERDICT_COLUMNS)
        for i, ex in enumerate(items, 1):
            qa = ex["qa"]
            w.writerow([i, ex["id"], split, status[ex["id"]], qa["question"], str(qa["answer"]).strip(),
                        qa["exe_ans"], qa["program"]] + [""] * len(VERDICT_COLUMNS))
    with open(OUT / f"{check}.md", "w", encoding="utf-8") as f:
        f.write(f"# {check}: {split}, status in {list(statuses)}, {len(items)} of {len(pool)} items, seed {SEED}\n\n")
        f.write("\n".join(item_md(i, ex, status[ex["id"]]) for i, ex in enumerate(items, 1)))
    print(f"{check}: wrote {len(items)} items (pool {len(pool)}) to {csv_path.name} and {check}.md")


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in CHECKS:
        sys.exit(f"usage: python -m finqa_lora.handcheck {{{'|'.join(CHECKS)}}}")
    build(sys.argv[1])
