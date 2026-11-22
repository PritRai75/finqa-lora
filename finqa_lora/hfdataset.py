"""The hand-checked FinQA items as a Hugging Face dataset (decision 57), and its upload.

Two files, both built from committed sheets and nothing else:
  hand_checks.csv                 every row of check1, check2 and check3 (198), first-pass verdict columns as
                                  committed, `uncertain` as true/false, and for the 20 re-checked items
                                  (decisions 54, 55) the second-pass verdict, uncertain flag and note
  error_analysis_gold_wrong.csv   the 13 test items tagged `gold_wrong` in the `other` hand tags (decision 53)
                                  that no hand-check covered: found with a model prediction in view, no
                                  corrected program, and in no audit count (open item 6)
The card is hub/dataset/README.md, written by hand and tested against results/.

Usage: python -m finqa_lora.hfdataset            builds both files into hub/dataset/ (needs a finished re-check)
       python -m finqa_lora.hfdataset --upload   uploads the committed card and files, downloads them back and
                                                 compares hashes; writes results/hub/dataset_upload.json
The token comes from the environment (HF_TOKEN); this module never reads, prints or writes it.
"""
import csv
import io
import json
import sys

from finqa_lora import REPO_ROOT, hub, recheck

REPO_ID = "PritRai75/finqa-label-audit"
OUT = REPO_ROOT / "hub" / "dataset"
CARD = "hub/dataset/README.md"
CHECKS_FILE, EXTRA_FILE = "hand_checks.csv", "error_analysis_gold_wrong.csv"
RECORD = REPO_ROOT / "results" / "hub" / "dataset_upload.json"
TAG_SHEET = REPO_ROOT / "handcheck" / "tag_other.csv"

CHECK_COLUMNS = ["check", "item", "id", "split", "screen_status", "question", "written_answer", "exe_ans",
                 "gold_program", "verdict", "wrong_side", "error_type", "corrected_answer", "corrected_program",
                 "uncertain", "note", "recheck_verdict", "recheck_uncertain", "recheck_note"]
EXTRA_COLUMNS = ["id", "split", "screen_status", "question", "written_answer", "exe_ans", "gold_program",
                 "tag", "shown_pass", "pred_program", "pred_value", "note"]


def flag(value):
    return "true" if value.strip() == "true" else "false"


def check_rows(second=None):
    """Rows of hand_checks.csv. second: {id: re-check row}, all 20 with a verdict."""
    if second is None:
        rep = recheck.validate()
        if rep["invalid"] or rep["with_verdict"] < rep["rows"]:
            raise ValueError("the re-check sheet is not finished and valid: run python -m finqa_lora.recheck --validate")
        second = {r["id"]: r for r in recheck.read()}
    first = recheck.first_pass()
    if set(second) != set(recheck.draw(first)):
        raise ValueError("the re-check rows are not the 20 drawn items")
    rows = []
    for check in recheck.FIRST_PASS:
        for i, (c, r) in first.items():
            if c != check:
                continue
            s = second.get(i)
            rows.append({
                "check": check, "item": r["item"], "id": i, "split": r["split"], "screen_status": r["screen_status"],
                "question": r["question"], "written_answer": r["answer"], "exe_ans": r["exe_ans"],
                "gold_program": r["program"],
                **{k: r[k].strip() for k in ("verdict", "wrong_side", "error_type", "corrected_answer",
                                             "corrected_program")},
                "uncertain": flag(r["uncertain"]), "note": r["note"].strip(),
                "recheck_verdict": s["verdict"].strip() if s else "",
                "recheck_uncertain": flag(s["uncertain"]) if s else "",
                "recheck_note": s["note"].strip() if s else "",
            })
    return rows


def extra_rows():
    """The `gold_wrong` hand tags on items that no hand-check covered."""
    first = recheck.first_pass()
    with open(TAG_SHEET, encoding="utf-8-sig", newline="") as f:
        tagged = [r for r in csv.DictReader(f) if r["tag"].strip() == "gold_wrong" and r["id"] not in first]
    return [{"id": r["id"], "split": r["split"], "screen_status": r["screen_status"], "question": r["question"],
             "written_answer": r["answer"], "exe_ans": r["exe_ans"], "gold_program": r["program"],
             "tag": "gold_wrong", "shown_pass": r["shown_pass"], "pred_program": r["pred_program"],
             "pred_value": r["pred_value"], "note": r["note"].strip()} for r in tagged]


def to_csv(rows, columns):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=columns, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue().encode("utf-8")


def built(second=None):
    return {CHECKS_FILE: to_csv(check_rows(second), CHECK_COLUMNS), EXTRA_FILE: to_csv(extra_rows(), EXTRA_COLUMNS)}


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    for name, data in built().items():
        (OUT / name).write_bytes(data)
        rows = data.count(b"\n") - 1
        print(f"wrote hub/dataset/{name} ({rows} rows)")


def upload_files():
    """The committed card and data files, after checking the data files are what the code builds."""
    files = {"README.md": hub.committed(CARD)}
    for name, data in built().items():
        committed = hub.committed(f"hub/dataset/{name}")
        if committed != data:
            raise hub.HubCheckFailed(f"hub/dataset/{name} at HEAD is not what the code builds: rebuild and commit")
        files[name] = committed
    return files


def main():
    args = sys.argv[1:]
    try:
        if args == []:
            build()
        elif args == ["--upload"]:
            files = upload_files()
            head = hub.publish_checks((CARD, f"hub/dataset/{CHECKS_FILE}", f"hub/dataset/{EXTRA_FILE}"))
            r = hub.upload_verified(REPO_ID, "dataset", files, f"Hand-checked FinQA items from finqa-lora {head[:7]}",
                                    f"https://github.com/PritRai75/finqa-lora/tree/{head}")
            r = {**{k: r[k] for k in ("repo_id", "hub_commit", "hub_commit_url", "visibility")}, "git_commit": head,
                 **{k: r[k] for k in ("files", "downloaded_back_identical", "huggingface_hub", "uploaded")}}
            RECORD.parent.mkdir(parents=True, exist_ok=True)
            with open(RECORD, "w", encoding="utf-8", newline="\n") as f:
                json.dump(r, f, indent=2)
                f.write("\n")
            print(f"uploaded and verified: {r['hub_commit_url']} ({r['visibility']})")
            print(f"wrote {RECORD.relative_to(REPO_ROOT).as_posix()}")
        else:
            sys.exit("usage: python -m finqa_lora.hfdataset [--upload]")
    except (ValueError, hub.HubCheckFailed) as e:
        sys.exit(f"refused: {e}")


if __name__ == "__main__":
    main()
