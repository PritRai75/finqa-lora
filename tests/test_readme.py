"""The README's test results are the committed results: every count, interval and example output in the
"Results" section is read back from the README and compared with results/ (so an edit to either fails CI)."""
import csv
import json
import re

import pytest

from finqa_lora import REPO_ROOT
from finqa_lora.data import load_split

README = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
RESULTS = README.split("## Results (test, 1,147 items)", 1)[1].split("\n## Status", 1)[0]
EVAL = json.loads((REPO_ROOT / "results/test/run1/evaluation.json").read_text(encoding="utf-8"))
VIEWS = ("official", "consistent", "corrected")


def row(label):
    """The cells of the results-table row that starts with label."""
    lines = [l for l in RESULTS.splitlines() if l.startswith(f"| {label} |")]
    assert len(lines) == 1, label
    return [c.strip() for c in lines[0].strip("|").split("|")][1:]


def pct(x):
    return f"{100 * x:.1f}%"


def share(v):
    """'90% (79–96%)' from a share with its Wilson bounds."""
    return f"{100 * v['share']:.0f}% ({100 * v['wilson_low']:.0f}–{100 * v['wilson_high']:.0f}%)"


def pt(x):
    return f"{100 * x:+.2f}".replace("-", "−")


def test_section_exists_and_view_sizes():
    assert EVAL["items"] == {"official": 1147, "consistent": 1046, "corrected": 1139}
    for view in VIEWS:
        assert f"{view} (of {EVAL['items'][view]:,})" in RESULTS


@pytest.mark.parametrize("arm", ["cleaned", "random"])
def test_adapter_rows(arm):
    cells = row(f"LoRA, {arm} arm, seeds 1–5")
    means = [l for l in RESULTS.splitlines() if l.startswith("| mean |")]
    mean_cells = [c.strip() for c in means[0 if arm == "cleaned" else 1].strip("|").split("|")][1:]
    for i, view in enumerate(VIEWS):
        acc = EVAL["views"][view]["accuracy"]
        assert cells[i] == ", ".join(str(acc[f"adapter:{arm}:{s}"]["correct"]) for s in range(1, 6))
        assert mean_cells[i] == pct(EVAL["views"][view]["arm_mean"][arm])


@pytest.mark.parametrize("label, name", [("Qwen2.5-1.5B-Instruct, 0-shot", "base:qwen2.5-1.5b:0"),
                                         ("Qwen2.5-1.5B-Instruct, 4-shot", "base:qwen2.5-1.5b:4"),
                                         ("Qwen3-4B-Instruct-2507, 4-shot", "base:qwen3-4b:4")])
def test_base_rows(label, name):
    for cell, view in zip(row(label), VIEWS):
        a = EVAL["views"][view]["accuracy"][name]
        lo, hi = (f"{100 * a[k]:.1f}" for k in ("wilson_low", "wilson_high"))
        assert cell == f"{a['correct']} = {pct(a['accuracy'])} ({lo}–{hi}%)"


@pytest.mark.parametrize("view", VIEWS)
def test_cleaned_vs_random_row(view):
    r = EVAL["views"][view]["cleaned_vs_random"]
    assert r["verdict"] == "no detectable difference" and r["rule"] == "variance_components"
    assert r["low"] < 0 < r["high"]   # the interval includes zero, hence the verdict
    assert row(view) == [f"{pt(r['difference'])} pt", f"{pt(r['low'])} to {pt(r['high'])}",
                         ", ".join(pt(d) for d in r["seed_pair_differences"]), r["verdict"]]


def test_finetuned_beats_every_base_in_every_view():
    for view in VIEWS:
        for base, r in EVAL["views"][view]["finetuned_vs_base"].items():
            assert r["verdict"] == "fine-tuning beats the base", (view, base)
    q = EVAL["views"]["official"]["finetuned_vs_base"]["base:qwen3-4b:4"]
    a = [x["a_only"] for x in q["per_adapter"].values()]
    b = [x["b_only"] for x in q["per_adapter"].values()]
    assert f"right on {min(a)}–{max(a)} items" in RESULTS and f"wrong on {min(b)}–{max(b)}" in RESULTS
    assert f"p ≤ {q['p_max']:.1e}".replace("e-0", "e-") in RESULTS


def test_side_statistics():
    r = EVAL["views"]["official"]["cleaned_vs_random"]
    item, two = r["item_bootstrap"], r["two_level_bootstrap"]
    assert f"{pt(item['low'])} to {pt(item['high'])} pt" in RESULTS
    assert f"{pt(two['low'])} to {pt(two['high'])} pt" in RESULTS
    assert f"({100 * r['seed_sd']:.2f} pt SD on test)" in RESULTS


def test_audit_numbers():
    c = json.loads((REPO_ROOT / "results/audit/counts.json").read_text(encoding="utf-8"))
    p1, p2 = c["check1"]["precision"], c["check2"]["precision_disagree"]
    assert (p1["count"], p1["of"], p2["count"], p2["of"]) == (45, 50, 68, 74)
    assert f"{p2['count']} of {p2['of']} = {p2['share']:.0%}" in RESULTS
    assert f"precision {share(p1)}" in RESULTS
    t = c["test_set"]
    assert f"{t['confirmed']} label problems confirmed; estimate {t['estimate']:.0f}; 95% upper bound " \
           f"{t['upper95']:.0f}" in RESULTS
    assert c["check1"]["wrong_side"] == {"answer": 14, "both": 3, "program": 28}


def test_hand_tag_table():
    o = json.loads((REPO_ROOT / "results/errors/other_tags.json").read_text(encoding="utf-8"))
    assert (o["sample"], o["pool"], o["seed"]) == (50, 266, 20261120)
    shown = {"gold_wrong": 1, "wrong_quantity": 2, "missing_step": 3, "extra_step": 4}
    table = [l for l in RESULTS.split("| Hand tag |", 1)[1].splitlines()[2:7]]
    for tag, i in shown.items():
        v = o["tags"][tag]
        cells = [c.strip() for c in table[i - 1].strip("|").split("|")]
        assert cells[1:] == [str(v["items"]), share(v)]
    assert all(o["tags"][t]["items"] == 0 for t in ("invented_number", "wrong_constant", "unclear"))


def test_example_outputs_are_the_rule_and_as_returned():
    rows = list(csv.DictReader(open(REPO_ROOT / "results/test/run1/cleaned/seed3/test.csv", encoding="utf-8",
                                    newline="")))
    assert [r["id"] for r in rows] == [ex["id"] for ex in load_split("test")]
    first, first_wrong = rows[0], next(r for r in rows if r["exe_correct"] == "0")
    assert (first["id"], first["exe_correct"], first_wrong["id"]) == \
        ("ETR/2016/page_23.pdf-2", "1", "SYY/2006/page_71.pdf-1")
    blocks = re.findall(r"```\n(.*?)\n```", RESULTS, re.S)
    assert blocks == [first["reply"], first_wrong["reply"]]


def test_trainable_parameters():
    hidden, mlp, layers, kv, r = 1536, 8960, 28, 2 * 128, 16
    per_layer = r * ((hidden + hidden) * 2 + (hidden + kv) * 2 + (hidden + mlp) * 3)
    assert layers * per_layer == 18_464_768 and "18,464,768 trainable parameters" in RESULTS
    report = json.loads((REPO_ROOT / "results/main/run1/report.json").read_text(encoding="utf-8"))
    size = report["runs"][0]["adapter_bytes"]
    assert 0 < size - 4 * layers * per_layer < 100_000   # fp32 tensors plus the safetensors header
