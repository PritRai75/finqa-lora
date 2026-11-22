"""Self-agreement re-check of the hand-check verdicts (decision 54, fixed by Prit on 22 Nov 2026, before the draw).

Population: every row of check1, check2 and check3 that is not `uncertain` in the first pass, 192 of 198
(131 real_error, 61 other verdicts). Uncertain rows are skipped because auditcounts.agreement leaves them
out anyway.
Draw: random.Random(20261127): 10 of the real_error rows, then 10 of the others, each from the ids in
sorted order; the 20 are then shuffled with the same generator, so the sheet order does not show the strata.
Sheet: handcheck/recheck.csv, the columns of the first-pass sheets with the verdict columns empty, and
handcheck/recheck.md with the same context the first pass had. Neither shows a first verdict, a note or the
sheet an item came from. The screen status is shown, as it was in the first pass.
Timing (decision 55, Prit, 22 Nov 2026, before any verdict): filled on or after 22 Nov 2026, two days after the
last first-pass verdicts (check3, 20 Nov), not the week planned in handcheck/README.md, so that the project is
finished before the resume goes out. Reported as a two-day gap. Filled without opening check1-3.csv. The counts
refuse a sheet whose verdicts were committed before that date.
Counts: auditcounts.agreement (defined in S7 before any verdict): same verdict, with a Wilson interval and
Cohen's kappa, on the five verdicts and on real_error versus not; rows uncertain in either pass left out.

Usage: python -m finqa_lora.recheck              builds the sheet (never overwrites one)
       python -m finqa_lora.recheck --validate   checks a filled sheet (exit 1 when a value is invalid)
       python -m finqa_lora.recheck --counts     counts a finished sheet: results/audit/self_agreement.json
"""
import csv
import json
import random
import subprocess
import sys

from finqa_lora import REPO_ROOT
from finqa_lora.auditcounts import agreement
from finqa_lora.data import load_split
from finqa_lora.handcheck import OUT, SHEET_COLUMNS, VERDICT_COLUMNS, check_row, item_md, screen_status

SEED = 20261127
N_REAL, N_OTHER = 10, 10
FIRST_PASS = ("check1", "check2", "check3")
NOT_BEFORE = "2026-11-22"     # decision 55 (was 2026-11-27 under decision 54)
NAME = "recheck"
FIRST_DIR = OUT                    # where check1-3.csv are read from (tests redirect OUT only)
SHEET = OUT / f"{NAME}.csv"
OUT_FILE = REPO_ROOT / "results" / "audit" / "self_agreement.json"


def first_pass():
    """{id: (check, row)} for every row of the finished first-pass sheets."""
    rows = {}
    for check in FIRST_PASS:
        with open(FIRST_DIR / f"{check}.csv", encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                if r["id"] in rows:
                    raise ValueError(f"{r['id']} is in {rows[r['id']][0]} and {check}")
                rows[r["id"]] = (check, r)
    return rows


def population(rows=None):
    """(real_error ids, other ids), sorted, without rows uncertain in the first pass."""
    rows = rows or first_pass()
    kept = sorted(i for i, (_, r) in rows.items() if r["uncertain"].strip() != "true")
    if any(not rows[i][1]["verdict"].strip() for i in kept):
        raise ValueError("a first-pass row has no verdict")
    real = [i for i in kept if rows[i][1]["verdict"].strip() == "real_error"]
    return real, [i for i in kept if i not in set(real)]


def draw(rows=None):
    """The 20 ids in sheet order."""
    real, other = population(rows)
    rng = random.Random(SEED)
    ids = rng.sample(real, N_REAL) + rng.sample(other, N_OTHER)
    rng.shuffle(ids)
    return ids


def items_for(ids, rows):
    """(split, example, screen status) per id, from the item's own split."""
    data, status = {}, {}
    for split in sorted({rows[i][1]["split"] for i in ids}):
        data[split] = {ex["id"]: ex for ex in load_split(split)}
        status[split] = screen_status(split)
    out = []
    for i in ids:
        split = rows[i][1]["split"]
        out.append((split, data[split][i], status[split][i]))
    return out


def build():
    if SHEET.exists():
        sys.exit(f"{SHEET} exists and may hold verdicts. Not overwriting.")
    rows = first_pass()
    real, other = population(rows)
    ids = draw(rows)
    with open(SHEET, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(SHEET_COLUMNS)
        for n, (split, ex, status) in enumerate(items_for(ids, rows), 1):
            qa = ex["qa"]
            w.writerow([n, ex["id"], split, status, qa["question"], str(qa["answer"]).strip(),
                        qa["exe_ans"], qa["program"]] + [""] * len(VERDICT_COLUMNS))
    with open(OUT / f"{NAME}.md", "w", encoding="utf-8", newline="\n") as f:
        f.write(f"# {NAME}: blind re-check of {len(ids)} hand-checked items, seed {SEED} (decisions 54, 55)\n\n"
                f"Fill on or after {NOT_BEFORE}, without opening check1-3.csv. Same columns and rules as "
                f"the first pass (the decision guide); `uncertain` is allowed.\n\n")
        f.write("\n".join(item_md(n, ex, status) for n, (_, ex, status) in enumerate(items_for(ids, rows), 1)))
    print(f"{NAME}: wrote {len(ids)} items ({N_REAL} of {len(real)} real_error, {N_OTHER} of {len(other)} others) "
          f"to {SHEET.name} and {NAME}.md")


def read(path=None):
    with open(path or SHEET, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def validate(path=None):
    rows, first = read(path), first_pass()
    report = {"rows": len(rows), "with_verdict": 0, "invalid": [], "to_review": []}
    if rows and list(rows[0]) != SHEET_COLUMNS:
        report["invalid"].append(("-", "-", f"header changed: expected {SHEET_COLUMNS}"))
    ids = draw(first)
    if [r.get("id") for r in rows] != ids:
        report["invalid"].append(("-", "-", "the rows are not the 20 drawn items in sheet order"))
        return report
    for r, (split, ex, status) in zip(rows, items_for(ids, first)):
        bad, look = check_row(r, ex, split, status)
        report["with_verdict"] += bool((r.get("verdict") or "").strip())
        report["invalid"] += [(r["item"], r["id"], m) for m in bad]
        report["to_review"] += [(r["item"], r["id"], m) for m in look]
    return report


def committed_on(path=SHEET):
    """Date (YYYY-MM-DD, committer time) of the last commit of the sheet, or None if it has local changes."""
    rel = path.relative_to(REPO_ROOT).as_posix()
    run = lambda *a: subprocess.run(["git", *a], cwd=REPO_ROOT, capture_output=True, text=True)
    if run("status", "--porcelain", "--", rel).stdout.strip():
        return None
    out = run("log", "-1", "--format=%cs", "--", rel).stdout.strip()
    return out or None


def counts(path=None, date=None):
    """Self-agreement of a finished, valid sheet whose verdicts were committed on or after NOT_BEFORE."""
    rep = validate(path)
    if rep["invalid"]:
        raise ValueError(f"{len(rep['invalid'])} invalid values: run --validate")
    if rep["with_verdict"] < rep["rows"]:
        raise ValueError(f"{rep['rows'] - rep['with_verdict']} rows still without a verdict")
    date = date or committed_on()
    if date is None:
        raise ValueError("commit the filled sheet first: the counts read the commit date")
    if date < NOT_BEFORE:
        raise ValueError(f"verdicts committed {date}, before {NOT_BEFORE} (decision 55)")
    first = {i: r for i, (_, r) in first_pass().items()}
    second = {r["id"]: r for r in read(path)}
    out = {"decision": 54, "seed": SEED, "items": len(second), "drawn": {"real_error": N_REAL, "other": N_OTHER},
           "committed": date, **agreement(first, second)}
    out["changed"] = [{"id": i, "first": first[i]["verdict"].strip(), "second": second[i]["verdict"].strip()}
                      for i in second if first[i]["verdict"].strip() != second[i]["verdict"].strip()]
    return out


def main():
    args = sys.argv[1:]
    if args == []:
        build()
    elif args == ["--validate"]:
        r = validate()
        print(f"{NAME}: {r['rows']} rows, {r['with_verdict']} with a verdict, {r['rows'] - r['with_verdict']} to do")
        for title, key in (("Invalid (fix before committing)", "invalid"), ("To review (may be right)", "to_review")):
            print(f"{title}: {len(r[key])}")
            for item, id_, msg in r[key]:
                print(f"  item {item}  {id_}  {msg}")
        sys.exit(1 if r["invalid"] else 0)
    elif args == ["--counts"]:
        try:
            c = counts()
        except ValueError as e:
            sys.exit(f"refused: {e}")
        OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(OUT_FILE, "w", encoding="utf-8", newline="\n") as f:
            json.dump(c, f, indent=2)
            f.write("\n")
        for name in ("verdict", "real_error"):
            s = c[name]
            print(f"same {name}: {s['count']}/{s['of']} = {s['share']:.0%} "
                  f"({s['wilson_low']:.0%}-{s['wilson_high']:.0%}), kappa {s['kappa']:.2f}")
        print(f"wrote {OUT_FILE.relative_to(REPO_ROOT).as_posix()}")
    else:
        sys.exit("usage: python -m finqa_lora.recheck [--validate | --counts]")


if __name__ == "__main__":
    main()
