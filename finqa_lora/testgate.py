"""Test gate: no model sees the test split until the test hand-checks are finished and committed.

Rules fixed before any test-set number exists (spec section 4): final test inference refuses to start
until check2 (every flagged test item) and check3 (50 unflagged test items) have a verdict on every
row, pass the validator with no invalid value, and are committed to git unchanged. This keeps the
hand-check blind to model predictions on test items.

open_gate() returns a record of the sheets it accepted (rows, verdict counts, git blob id, last
commit that touched each), which every test pass stores beside its predictions. The record shows that the verdicts
existed, in that exact form, before the predictions were made.

There is no override. finqa_lora.infer.run calls open_gate() for split "test".

Usage: python -m finqa_lora.testgate      (prints the state of the gate; exit 1 while closed)
"""
import csv
import subprocess
import sys

from finqa_lora import REPO_ROOT

TEST_CHECKS = ("check2", "check3")


class GateClosed(RuntimeError):
    pass


def _git(*args, root=REPO_ROOT):
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)


def sheet_problems(check, root=REPO_ROOT):
    """Everything that keeps one sheet from opening the gate. Empty list = the sheet is ready."""
    from finqa_lora import handcheck

    rel = f"handcheck/{check}.csv"
    path = root / rel
    if not path.exists():
        return [f"{rel} does not exist yet"]
    problems = []
    report = handcheck.validate(check, path=path)
    if report["invalid"]:
        problems.append(f"{rel}: {len(report['invalid'])} invalid values (run: python -m finqa_lora.handcheck "
                        f"{check} --validate)")
    empty = report["rows"] - report["with_verdict"]
    if empty:
        problems.append(f"{rel}: {empty} of {report['rows']} rows have no verdict")
    items, _, _ = handcheck.select_items(check)
    if report["ids"] != [ex["id"] for ex in items]:
        problems.append(f"{rel}: items differ from the ones the sheet was built with (row added, removed or moved)")
    tracked = _git("ls-files", "--error-unmatch", rel, root=root)
    if tracked.returncode != 0:
        problems.append(f"{rel} is not committed")
    else:
        dirty = _git("status", "--porcelain", "--", rel, root=root)
        if dirty.returncode != 0 or dirty.stdout.strip():
            problems.append(f"{rel} has changes that are not committed")
    return problems


def sheet_record(check, root=REPO_ROOT):
    """What a test pass stores about a sheet it was allowed through by.

    git_blob is git's id of the committed file, the same on every platform (a Windows checkout with
    core.autocrlf has CRLF line endings on disk, so a hash of the disk bytes would differ).
    """
    from finqa_lora import handcheck

    rel = f"handcheck/{check}.csv"
    with open(root / rel, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    verdicts = {}
    for r in rows:
        verdicts[r["verdict"]] = verdicts.get(r["verdict"], 0) + 1
    log = _git("log", "-1", "--format=%H %cI", "--", rel, root=root).stdout.split()
    return {"sheet": rel, "rows": len(rows), "verdicts": dict(sorted(verdicts.items())),
            "git_blob": _git("rev-parse", f"HEAD:{rel}", root=root).stdout.strip(),
            "last_commit": log[0] if log else None, "last_commit_date": log[1] if len(log) > 1 else None,
            "allowed_verdicts": list(handcheck.VERDICTS)}


def open_gate(root=REPO_ROOT):
    """Return the record of the accepted sheets, or raise GateClosed listing every problem."""
    if _git("rev-parse", "--is-inside-work-tree", root=root).returncode != 0:
        raise GateClosed("the test gate needs a git checkout of the repo, to see that the sheets are committed")
    problems = [p for c in TEST_CHECKS for p in sheet_problems(c, root)]
    if problems:
        raise GateClosed("test split locked until check2 and check3 are finished and committed:\n  "
                         + "\n  ".join(problems))
    return {c: sheet_record(c, root) for c in TEST_CHECKS}


def main():
    try:
        record = open_gate()
    except GateClosed as e:
        print(f"CLOSED: {e}")
        sys.exit(1)
    print("OPEN")
    for check, r in record.items():
        print(f"  {check}: {r['rows']} rows {r['verdicts']}, blob {r['git_blob'][:12]}, "
              f"last commit {r['last_commit'][:7]} {r['last_commit_date']}")


if __name__ == "__main__":
    main()
