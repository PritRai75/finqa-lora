"""Automatic screen: does each gold program agree with the annotator's written answer?

For every item the official executor runs the gold program (it must reproduce exe_ans),
then the written `answer` string is parsed and compared with exe_ans. The comparison is
lenient: it allows a percent written as a fraction (x100 or /100) and rounding to the
answer's own decimals, with a floor of 0.5% relative difference.

Status per item:
  agree       program result and written answer match
  sign_only   they match only after dropping the sign (a decline written as a positive number)
  disagree    they do not match: a flag for the hand-check
  unparsed    the written answer is free text the parser cannot read
  no_answer   the written answer is empty
  exe_error   the gold program does not run, or does not reproduce exe_ans (none expected)

This is a screen, not a verdict. Whether a flag is a real label error, and which side is
wrong, is decided by hand (see handcheck/).

Usage: python -m finqa_lora.screen
"""
import csv
import json
import re
from collections import Counter

from finqa_lora import REPO_ROOT, SPLITS
from finqa_lora.data import load_split
from finqa_lora.scoring import execute

PARSER_VERSION = 1
OUT_DIR = REPO_ROOT / "results" / "screen"

_UNITS = r"(?:million|billion|thousand|years?|days?|times)"
_NUM = re.compile(r"(-?)(\d+\.?\d*|\.\d+)\s*(%?)\s*" + _UNITS + r"?")


def parse_answer(raw):
    """Written answer -> ('yes'|'no', None) | (float, decimals) | (None, None) if unreadable.

    v1 over the first checker: removes literal '\\n' and real newlines, reads '.5' and '5.%',
    strips a trailing full stop, and reads '( 5.2 )' as -5.2.
    """
    s = re.sub(r"\\+n", " ", str(raw).lower()).replace("\n", " ")
    s = s.replace(",", "").replace("$", "").strip().rstrip(".").strip()
    if s in ("yes", "no"):
        return s, None
    neg = False
    m = re.fullmatch(r"\(\s*(.+?)\s*\)", s)
    if m:
        s, neg = m.group(1), True
    m = _NUM.fullmatch(s)
    if not m:
        return None, None
    digits = m.group(2)
    value = float(digits) * (-1 if (m.group(1) == "-") != neg else 1)
    decimals = len(digits.split(".")[1]) if "." in digits else 0
    return value, decimals


def compare(exe_ans, raw_answer):
    """Return one of: agree, sign_only, disagree, unparsed, no_answer."""
    if not str(raw_answer).strip():
        return "no_answer"
    value, decimals = parse_answer(raw_answer)
    if value is None:
        return "unparsed"
    if isinstance(value, str) or isinstance(exe_ans, str):
        return "agree" if str(value) == str(exe_ans) else "disagree"

    def close(x, a):
        tol = max(0.5 * 10 ** (-decimals) + 1e-9, 0.005 * abs(a))
        return any(abs(c - a) <= tol for c in (x, x * 100, x / 100))

    if close(exe_ans, value):
        return "agree"
    if close(abs(exe_ans), abs(value)):
        return "sign_only"
    return "disagree"


def screen_item(ex):
    qa = ex["qa"]
    ok, value = execute(qa["program"], ex["table"])
    if not ok or value != qa["exe_ans"]:
        return "exe_error"
    return compare(qa["exe_ans"], qa["answer"])


def run():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    summary = {"parser_version": PARSER_VERSION, "splits": {}}
    for split in SPLITS:
        data = load_split(split)
        counts = Counter()
        with open(OUT_DIR / f"{split}.csv", "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["id", "status", "exe_ans", "answer"])
            for ex in data:
                status = screen_item(ex)
                counts[status] += 1
                w.writerow([ex["id"], status, ex["qa"]["exe_ans"], str(ex["qa"]["answer"]).strip()])
        summary["splits"][split] = {"items": len(data), **dict(sorted(counts.items()))}
        print(split, summary["splits"][split])
    with open(OUT_DIR / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    run()
