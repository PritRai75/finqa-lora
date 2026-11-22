"""The HF dataset of the hand-checked items (decision 57): the committed files are what the code builds from the
committed sheets, the 13 error-analysis items are the ones open item 6 describes, the card's numbers are the
committed counts, and the upload sends the committed bytes and checks them on the way back (fake Hub)."""
import csv
import hashlib
import io
import json
import re
import sys
import types
from pathlib import Path

import pytest

from finqa_lora import REPO_ROOT, hfdataset, hub, recheck

CARD = (REPO_ROOT / hfdataset.CARD).read_text(encoding="utf-8")
FLAT = " ".join(CARD.split())


def load(path):
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def rows_of(data):
    return list(csv.DictReader(io.StringIO(data.decode("utf-8"))))


@pytest.fixture(scope="module")
def built():
    return hfdataset.built()


def test_committed_files_are_the_build(built):
    for name, data in built.items():
        assert (hfdataset.OUT / name).read_bytes() == data, name


def test_hand_checks_rows(built):
    rows = rows_of(built[hfdataset.CHECKS_FILE])
    assert list(rows[0]) == hfdataset.CHECK_COLUMNS and len(rows) == 198
    assert [r["check"] for r in rows] == ["check1"] * 50 + ["check2"] * 98 + ["check3"] * 50
    assert sum(r["uncertain"] == "true" for r in rows) == 6 and {r["uncertain"] for r in rows} == {"true", "false"}
    second = {r["id"]: r for r in recheck.read()}
    for r in rows:
        if r["id"] in second:
            assert r["recheck_verdict"] == second[r["id"]]["verdict"].strip() != ""
            assert r["recheck_uncertain"] in ("true", "false")
        else:
            assert r["recheck_verdict"] == r["recheck_uncertain"] == r["recheck_note"] == ""
    assert sum(bool(r["recheck_verdict"]) for r in rows) == 20
    first = recheck.first_pass()
    for r in rows:   # the first-pass verdict columns as committed
        f = first[r["id"]][1]
        assert (r["verdict"], r["note"], r["gold_program"]) == (f["verdict"].strip(), f["note"].strip(), f["program"])


def test_error_analysis_rows(built):
    rows = rows_of(built[hfdataset.EXTRA_FILE])
    assert list(rows[0]) == hfdataset.EXTRA_COLUMNS and len(rows) == 13
    first = recheck.first_pass()
    assert all(r["id"] not in first and r["screen_status"] == "agree" and r["tag"] == "gold_wrong" for r in rows)
    tags = load("results/errors/other_tags.json")["tags"]["gold_wrong"]["items"]
    with open(hfdataset.TAG_SHEET, encoding="utf-8-sig", newline="") as f:
        gw = [r["id"] for r in csv.DictReader(f) if r["tag"].strip() == "gold_wrong"]
    assert len(gw) == tags == 20 and len([i for i in gw if i in first]) == 7
    assert all(first[i][1]["verdict"] == "real_error" for i in gw if i in first)


def test_card_configs_and_columns():
    head = CARD.split("---\n")[1]
    assert "license: mit" in head and f"data_files: {hfdataset.CHECKS_FILE}" in head
    assert f"data_files: {hfdataset.EXTRA_FILE}" in head
    for col in hfdataset.CHECK_COLUMNS:
        assert f"`{col}`" in CARD, col
    assert f'load_dataset("{hfdataset.REPO_ID}", "hand_checks"' in CARD
    assert "| `hand_checks` (default) | 198 |" in CARD and "| `error_analysis_gold_wrong` | 13 |" in CARD
    assert f"commit `{load('data/manifest.json')['commit'][:7]}`" in CARD


def pct(s):
    """'90% (79–96%)' from a share with its Wilson bounds."""
    return f"{s['share']:.0%} ({100 * s['wilson_low']:.0f}–{100 * s['wilson_high']:.0f}%)"


def test_card_results():
    c = load("results/audit/counts.json")
    k1, k2, k3, t = c["check1"], c["check2"], c["check3"], c["test_set"]
    p1 = k1["verdicts"]["real_error"]
    assert f"45 of 50 flags are real label problems: {pct(p1)}" in CARD
    assert (p1["count"], k1["kinds"]["wrong_program"]["count"], k1["kinds"]["wrong_written_answer"]["count"]) == (45, 31, 17)
    p2 = k2["precision_disagree"]
    assert f"on `disagree` items {p2['count']} of {p2['of']} = {pct(p2)}" in CARD
    assert (k2["verdicts"]["real_error"]["count"], k2["counted"], k2["uncertain"]) == (83, 94, 4)
    assert k2["kinds"]["missing_answer"]["count"] == 11
    m = k3["misses"]
    assert (m["count"], m["of"]) == (3, 48) and f"upper bound {100 * m['upper95_one_sided']:.1f}%" in CARD
    assert f"| Test set | {t['confirmed']} confirmed; estimate {t['estimate']:.0f}; 95% upper bound {t['upper95']:.0f} of 1,147 |" in CARD


def test_card_self_agreement():
    a = load("results/audit/self_agreement.json")
    assert "SELF_AGREEMENT" not in CARD
    for name in ("verdict", "real_error"):
        s = a[name]
        assert f"{s['count']} of {s['of']}" in FLAT and f"kappa {s['kappa']:.2f}" in FLAT, name
    assert "two days after the first pass" in FLAT and "decision 55" in FLAT


def test_upload_refuses_data_that_is_not_the_build(monkeypatch):
    # The working-tree files stand in for the committed ones (pytest runs before the commit), one of them altered.
    monkeypatch.setattr(hub, "committed",
                        lambda p: b"x" if p.endswith(hfdataset.EXTRA_FILE) else (REPO_ROOT / p).read_bytes())
    with pytest.raises(hub.HubCheckFailed, match="not what the code builds"):
        hfdataset.upload_files()


def test_upload_goes_to_a_dataset_repo_and_checks_the_copy(monkeypatch):
    store, calls = {}, []

    class Api:
        def whoami(self):
            return {"name": "PritRai75"}

        def create_repo(self, repo_id, **kw):
            calls.append((repo_id, kw))

        def upload_folder(self, repo_id, folder_path, **kw):
            store.update({p.name: p.read_bytes() for p in Path(folder_path).iterdir()})
            return types.SimpleNamespace(oid="d00d", commit_url=f"https://huggingface.co/datasets/{repo_id}/commit/d00d")

        def dataset_info(self, repo_id):
            return types.SimpleNamespace(private=False)

    def download(repo_id, name, revision, cache_dir, repo_type="model"):
        assert repo_type == "dataset" and revision == "d00d"
        path = Path(cache_dir) / name
        path.write_bytes(store[name])
        return str(path)

    monkeypatch.setitem(sys.modules, "huggingface_hub",
                        types.SimpleNamespace(HfApi=Api, hf_hub_download=download, __version__="fake"))
    files = {"README.md": CARD.encode("utf-8"), **hfdataset.built()}
    r = hub.upload_verified(hfdataset.REPO_ID, "dataset", files, "m", "d")
    assert calls == [(hfdataset.REPO_ID, {"repo_type": "dataset", "private": False, "exist_ok": True})]
    assert r["visibility"] == "public" and sorted(r["files"]) == sorted(files)
    assert r["files"][hfdataset.CHECKS_FILE]["sha256"] == hashlib.sha256(files[hfdataset.CHECKS_FILE]).hexdigest()


def test_dataset_upload_record():
    """results/hub/dataset_upload.json is the upload of the committed card and files, checked by download-back.
    Edit the card or rebuild the files and this fails until they are uploaded again."""
    u = load("results/hub/dataset_upload.json")
    assert (u["repo_id"], u["visibility"], u["downloaded_back_identical"]) == (hfdataset.REPO_ID, "public", True)
    assert u["hub_commit"] == "4c602fa22a4245b1817aa8759d6decc1d365183c"
    assert u["hub_commit_url"].endswith(f"/datasets/{hfdataset.REPO_ID}/commit/{u['hub_commit']}")
    assert u["git_commit"] == "aa5056293f794a2b86acc2b7461b2b2e94757c8c"
    files = {"README.md": (REPO_ROOT / hfdataset.CARD).read_bytes(),
             **{n: (hfdataset.OUT / n).read_bytes() for n in (hfdataset.CHECKS_FILE, hfdataset.EXTRA_FILE)}}
    assert u["files"] == {n: {"bytes": len(d), "sha256": hashlib.sha256(d).hexdigest()} for n, d in files.items()}
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert f"Hub commit `{u['hub_commit'][:7]}` from repo commit `{u['git_commit'][:7]}`" in readme
