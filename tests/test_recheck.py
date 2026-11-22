"""The self-agreement re-check (decision 54): the draw follows the rule and is pinned, the committed sheet is
exactly what the code builds and shows no first-pass verdict, a filled sheet is validated like the first pass,
and the counts need a finished sheet committed on or after 22 Nov 2026 (decision 55)."""
import csv
import json
import hashlib

import pytest

from finqa_lora import recheck
from finqa_lora.handcheck import SHEET_COLUMNS, VERDICT_COLUMNS

DRAWN = ['JPM/2010/page_120.pdf-2', 'CDNS/2018/page_82.pdf-1', 'AON/2007/page_188.pdf-2', 'PNC/2012/page_65.pdf-5',
         'ETR/2016/page_23.pdf-1', 'UNP/2011/page_24.pdf-3', 'IPG/2015/page_24.pdf-3', 'GIS/2019/page_68.pdf-1',
         'HUM/2009/page_105.pdf-1', 'STT/2009/page_127.pdf-2', 'PNC/2014/page_111.pdf-2', 'ANSS/2012/page_93.pdf-4',
         'AON/2015/page_96.pdf-3', 'HWM/2017/page_42.pdf-2', 'ADBE/2008/page_74.pdf-3', 'UNP/2018/page_74.pdf-1',
         'HOLX/2005/page_27.pdf-2', 'AES/2001/page_85.pdf-2', 'CME/2010/page_69.pdf-1', 'MRO/2004/page_46.pdf-4']


# The first pass as committed (check1 cc61253, check2 e467ff5, check3 5aa1573): the baseline the re-check is
# compared with, so a later edit to a first-pass sheet fails here instead of moving the baseline.
FIRST_PASS_SHA256 = {
    "check1": "3f88f9849342ccd2c912e6315d734913d7877c88d9c47fac9bd6df1f75288ded",
    "check2": "1c4cbb8d9373ffec75e6a1e86d7df42fc7f32418b282c7139fdfe1e73a823d60",
    "check3": "50afefcd984d3f675f2763a0b98dea8f4ee628c2cc5d40a1327de7eec72e7d1d",
}


@pytest.fixture(scope="module")
def first():
    return recheck.first_pass()


def test_design_is_pinned():
    assert (recheck.SEED, recheck.N_REAL, recheck.N_OTHER) == (20261127, 10, 10)
    assert recheck.FIRST_PASS == ("check1", "check2", "check3") and recheck.NOT_BEFORE == "2026-11-22"   # decision 55


def test_first_pass_sheets_are_unchanged():
    for check, sha in FIRST_PASS_SHA256.items():
        assert hashlib.sha256((recheck.FIRST_DIR / f"{check}.csv").read_bytes()).hexdigest() == sha, check


def test_population_skips_uncertain_rows(first):
    real, other = recheck.population(first)
    assert len(first) == 198 and (len(real), len(other)) == (131, 61)
    assert not set(real) & set(other) and real == sorted(real) and other == sorted(other)
    uncertain = {i for i, (_, r) in first.items() if r["uncertain"].strip() == "true"}
    assert len(uncertain) == 6 and not uncertain & (set(real) | set(other))
    assert all(first[i][1]["verdict"].strip() == "real_error" for i in real)
    assert all(first[i][1]["verdict"].strip() != "real_error" for i in other)


def test_draw_is_ten_and_ten_and_pinned(first):
    ids = recheck.draw(first)
    assert ids == recheck.draw(first) == DRAWN and len(set(ids)) == 20
    real, other = recheck.population(first)
    assert len(set(ids) & set(real)) == 10 and len(set(ids) & set(other)) == 10


def test_committed_sheet_is_the_build(tmp_path, monkeypatch):
    committed = recheck.read()
    committed_csv, committed_md = recheck.SHEET.read_bytes(), (recheck.OUT / "recheck.md").read_bytes()
    monkeypatch.setattr(recheck, "OUT", tmp_path)
    monkeypatch.setattr(recheck, "SHEET", tmp_path / "recheck.csv")
    recheck.build()
    built = recheck.read(tmp_path / "recheck.csv")
    keep = [c for c in SHEET_COLUMNS if c not in VERDICT_COLUMNS]
    assert [{k: r[k] for k in keep} for r in committed] == [{k: r[k] for k in keep} for r in built]
    assert (tmp_path / "recheck.md").read_bytes() == committed_md
    if not any(r["verdict"].strip() for r in committed):    # before the re-check: byte for byte
        assert (tmp_path / "recheck.csv").read_bytes() == committed_csv


def test_sheet_shows_no_first_pass_verdict(first):
    md = (recheck.OUT / "recheck.md").read_text(encoding="utf-8")
    for i in DRAWN:
        note = first[i][1]["note"].strip()
        assert note and note not in md
    assert "verdict" not in md.split("\n## 1.")[1]   # the items carry no verdict text


def test_committed_sheet_has_no_invalid_values():
    """Gate, as for check1-3: verdicts can only be committed when every filled value follows the protocol."""
    report = recheck.validate()
    assert report["rows"] == 20 and report["invalid"] == [], report["invalid"]


def filled_copy(tmp_path, first, change=None):
    """The sheet filled with the first-pass verdict columns (a valid fill); change: {id: verdict columns}."""
    path = tmp_path / "recheck.csv"
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(SHEET_COLUMNS)
        for r in recheck.read():
            v = {k: first[r["id"]][1][k] for k in VERDICT_COLUMNS} | (change or {}).get(r["id"], {})
            w.writerow([r[k] for k in SHEET_COLUMNS if k not in VERDICT_COLUMNS] + [v[k] for k in VERDICT_COLUMNS])
    return path


def test_counts_of_an_identical_second_pass(tmp_path, first):
    c = recheck.counts(filled_copy(tmp_path, first), date="2026-11-27")
    assert c["items"] == 20 and c["changed"] == [] and c["left_out_uncertain"] == 0
    assert c["verdict"]["count"] == c["verdict"]["of"] == 20 and c["verdict"]["kappa"] == 1.0


def test_counts_report_a_changed_verdict(tmp_path, first):
    other = next(i for i in DRAWN if first[i][1]["verdict"].strip() == "no_error")
    note = first[other][1]["note"]
    c = recheck.counts(filled_copy(tmp_path, first, {other: {"verdict": "rounding", "note": note}}), date="2026-12-01")
    assert c["changed"] == [{"id": other, "first": "no_error", "second": "rounding"}]
    assert c["verdict"]["count"] == 19 and c["real_error"]["count"] == 20
    assert c["verdict"]["kappa"] < 1.0 and c["real_error"]["kappa"] == 1.0


def test_uncertain_in_the_second_pass_is_left_out(tmp_path, first):
    i = DRAWN[0]
    c = recheck.counts(filled_copy(tmp_path, first, {i: {"uncertain": "true"}}), date="2026-11-27")
    assert c["left_out_uncertain"] == 1 and c["verdict"]["of"] == 19


@pytest.mark.parametrize("problem", ["early", "uncommitted", "unfinished", "invalid", "order"])
def test_counts_refuse(tmp_path, first, monkeypatch, problem):
    date = "2026-11-27"
    if problem == "unfinished":
        path = filled_copy(tmp_path, first, {DRAWN[0]: {k: "" for k in VERDICT_COLUMNS}})
    elif problem == "invalid":
        path = filled_copy(tmp_path, first, {DRAWN[0]: {"verdict": "maybe"}})
    elif problem == "order":
        path = filled_copy(tmp_path, first)
        lines = path.read_text(encoding="utf-8-sig").splitlines(keepends=True)
        path.write_text(lines[0] + lines[2] + lines[1] + "".join(lines[3:]), encoding="utf-8-sig")
    else:
        path = filled_copy(tmp_path, first)
        if problem == "early":
            date = "2026-11-21"
        else:                                   # the sheet has local changes: committed_on gives None
            monkeypatch.setattr(recheck, "committed_on", lambda path=None: None)
            date = None
    with pytest.raises(ValueError):
        recheck.counts(path, date=date)


def test_committed_self_agreement_is_the_count():
    """results/audit/self_agreement.json is what --counts gives on the committed sheet (decisions 54, 55)."""
    path = recheck.OUT_FILE
    committed = json.loads(path.read_text(encoding="utf-8"))
    assert committed["committed"] >= recheck.NOT_BEFORE
    assert recheck.counts(date=committed["committed"]) == committed
    assert committed["items"] == 20 and committed["left_out_uncertain"] == 0
