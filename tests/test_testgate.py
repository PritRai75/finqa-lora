"""The test gate opens only for finished, valid, committed check2 and check3 sheets.

Each case builds a throwaway git repo holding the two sheets, filled from the real test items.
"""
import csv
import subprocess

import pytest

from finqa_lora import handcheck, testgate


def git(root, *args):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "core.autocrlf=false", *args],
                   cwd=root, check=True, capture_output=True)


def write_sheet(root, check, fill=True, drop=0):
    items, _, status = handcheck.select_items(check)
    path = root / "handcheck" / f"{check}.csv"
    path.parent.mkdir(exist_ok=True)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=handcheck.SHEET_COLUMNS, lineterminator="\n")
        w.writeheader()
        for n, ex in enumerate(items[drop:], 1):
            row = {"item": n, **handcheck.read_only_values(ex, "test", status[ex["id"]])}
            row.update({k: "" for k in handcheck.VERDICT_COLUMNS})
            if fill:
                row.update(verdict="no_error", note=f"Program gives {ex['qa']['exe_ans']}.")
            w.writerow(row)
    return path


@pytest.fixture
def repo(tmp_path):
    git(tmp_path, "init", "-q")
    for check in testgate.TEST_CHECKS:
        write_sheet(tmp_path, check)
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-q", "-m", "verdicts")
    return tmp_path


def closed_because(root):
    with pytest.raises(testgate.GateClosed) as e:
        testgate.open_gate(root)
    return str(e.value)


def test_finished_committed_sheets_open_the_gate(repo):
    record = testgate.open_gate(repo)
    assert set(record) == {"check2", "check3"}
    assert record["check2"]["rows"] == 98 and record["check3"]["rows"] == 50   # 76 + 8 + 14; 50 sampled
    assert record["check2"]["verdicts"] == {"no_error": 98}
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True).stdout.strip()
    assert record["check3"]["last_commit"] == head and len(record["check3"]["git_blob"]) == 40


def test_a_missing_sheet_keeps_it_closed(repo):
    git(repo, "rm", "-q", "handcheck/check3.csv")
    git(repo, "commit", "-q", "-m", "drop")
    assert "handcheck/check3.csv does not exist yet" in closed_because(repo)


def test_an_empty_verdict_keeps_it_closed(repo):
    write_sheet(repo, "check2", fill=False)
    git(repo, "commit", "-q", "-am", "unfill")
    assert "check2.csv: 98 of 98 rows have no verdict" in closed_because(repo)


def test_uncommitted_changes_keep_it_closed(repo):
    path = repo / "handcheck" / "check3.csv"
    path.write_bytes(path.read_bytes().replace(b"no_error", b"rounding", 1))   # bytes: no newline translation
    assert "check3.csv has changes that are not committed" in closed_because(repo)


def test_an_untracked_sheet_keeps_it_closed(tmp_path):
    git(tmp_path, "init", "-q")
    for check in testgate.TEST_CHECKS:
        write_sheet(tmp_path, check)
    message = closed_because(tmp_path)
    assert "check2.csv is not committed" in message and "check3.csv is not committed" in message


def test_a_removed_row_keeps_it_closed(repo):
    write_sheet(repo, "check2", drop=1)
    git(repo, "commit", "-q", "-am", "drop a row")
    assert "items differ from the ones the sheet was built with" in closed_because(repo)


def test_an_invalid_value_keeps_it_closed(repo):
    path = repo / "handcheck" / "check2.csv"
    path.write_bytes(path.read_bytes().replace(b"no_error", b"No_error", 1))
    git(repo, "commit", "-q", "-am", "typo")
    assert "check2.csv: 1 invalid values" in closed_because(repo)


def test_outside_a_git_checkout_it_stays_closed(tmp_path):
    for check in testgate.TEST_CHECKS:
        write_sheet(tmp_path, check)
    assert "needs a git checkout" in closed_because(tmp_path)


def test_test_inference_stops_before_loading_any_model(tmp_path, monkeypatch):
    """infer.run on test raises GateClosed, not a model-loading error, for a model that does not exist.
    The gate is closed here by pointing the real gate at a folder that is no git checkout, so this holds
    whatever this repo's own gate says (it opened in S7, when check3 was committed)."""
    pytest.importorskip("torch")
    from finqa_lora.infer import run
    real = testgate.open_gate
    monkeypatch.setattr(testgate, "open_gate", lambda root=None: real(tmp_path))
    with pytest.raises(testgate.GateClosed, match="needs a git checkout"):
        run("no/such-model", "test", limit=1)
