"""Test passes: the plan covers every model once, adapters are found only by the committed SHA-256,
the dev check uses decision 38's tolerance, and nothing runs while the test gate is closed."""
import csv
import json
import re
import subprocess
import sys

import pytest

from finqa_lora import REPO_ROOT, mainruns, testgate, testpass
from finqa_lora.pilot import sha256


def test_plan_runs_every_model_once_with_both_arms_on_each_gpu():
    passes = testpass.all_passes()
    assert len(passes) == 13 and len(set(passes)) == 13   # 10 adapters + 1.5B 0- and 4-shot + 4B 4-shot
    assert sorted(testpass.CHAINS[0] + testpass.CHAINS[1]) == sorted(passes)
    for gpu, chain in testpass.CHAINS.items():
        arms = {testpass.parse_pass(n).get("arm") for n in chain} - {None}
        assert arms == set(mainruns.ARMS), gpu
    gpu_of = {n: g for g, chain in testpass.CHAINS.items() for n in chain}
    for s in mainruns.SEEDS:   # the two arms of a seed run on different GPUs
        assert gpu_of[f"adapter:cleaned:{s}"] != gpu_of[f"adapter:random:{s}"]
    assert testpass.DEV_CHECK == {0: ("cleaned", 1), 1: ("random", 1)}


def test_job_file_takes_its_chains_from_the_module():
    job = (REPO_ROOT / "jobs" / "testpass.sh").read_text(encoding="utf-8")
    assert not re.search(r"(adapter|base):[a-z0-9.\-]+:\d", job)
    assert job.index("finqa_lora.testgate") < job.index("testpass locate") < job.index("testpass devcheck") \
        < job.index("testpass run")
    for gpu, chain in testpass.CHAINS.items():
        out = subprocess.run([sys.executable, "-m", "finqa_lora.testpass", "chain", "--gpu", str(gpu)],
                             cwd=REPO_ROOT, capture_output=True, text=True, check=True).stdout.split()
        assert out == chain


def test_unknown_pass_is_refused():
    for bad in ("adapter:cleaned:6", "adapter:full:1", "base:qwen3-4b:0", "base:llama:4"):
        with pytest.raises(ValueError, match="unknown pass"):
            testpass.parse_pass(bad)


def test_expected_adapters_are_the_ten_committed_runs():
    """Decision 41: the committed reports are the record of the adapters (main runs 1 and 2, 19 Nov)."""
    e = testpass.expected_adapters()
    assert sorted(e) == [(a, s) for a in mainruns.ARMS for s in mainruns.SEEDS]
    assert e[("cleaned", 1)]["sha256"] == "5491c76f946fd1d54649072ffd4c77cb85bc8f0b0536c8d80bb2283a329350ba"
    assert e[("random", 5)]["sha256"] == "5c87778023aaaf8277b27f33734d17536b8e01190f9cc3d8ee1f1613bf67772f"
    assert {x["bytes"] for x in e.values()} == {73911112}
    assert {x["run"] for x in e.values()} == {"run1", "run2"}
    assert all(x["config"].exists() and x["dev_csv"].exists() for x in e.values())


def test_base_revisions_are_the_ones_feasibility_recorded():
    rep = json.loads((REPO_ROOT / "results" / "feasibility" / "run1" / "report.json").read_text(encoding="utf-8"))
    for model, sha in testpass.BASE_REVISIONS.items():
        assert rep["candidates"][model]["licence"]["sha"] == sha


def fake_expected(tmp_path, n=3):
    """n fake adapters of equal size, their committed configs and dev files, and the expected map."""
    expected, files = {}, {}
    for k in range(1, n + 1):
        folder = tmp_path / "results" / "cleaned" / f"seed{k}"
        (folder / "adapter").mkdir(parents=True)
        (folder / "adapter" / "adapter_config.json").write_text(json.dumps({"r": 16, "k": k}))
        weights = tmp_path / "made" / f"w{k}.safetensors"
        weights.parent.mkdir(exist_ok=True)
        weights.write_bytes(bytes([k]) * 64)
        files[("cleaned", k)] = weights
        expected[("cleaned", k)] = {"sha256": sha256(weights), "bytes": 64, "run": "run1", "folder": folder,
                                    "config": folder / "adapter" / "adapter_config.json", "dev_csv": folder / "dev.csv"}
    return expected, files


def test_adapters_are_found_by_hash_whatever_their_names(tmp_path):
    expected, files = fake_expected(tmp_path)
    root = tmp_path / "input" / "some-dataset"
    (root / "deep").mkdir(parents=True)
    for i, (key, f) in enumerate(sorted(files.items())):
        (root / ("deep" if i else ".") / f"renamed-{i}.safetensors").write_bytes(f.read_bytes())
    (root / "other.safetensors").write_bytes(b"x" * 64)   # same size, unknown hash: ignored
    found = testpass.locate(tmp_path / "input", expected)
    assert sorted(found) == sorted(expected)
    assert all(sha256(found[k]) == expected[k]["sha256"] for k in expected)


def test_a_missing_or_changed_adapter_stops_the_job(tmp_path):
    expected, files = fake_expected(tmp_path)
    root = tmp_path / "input"
    root.mkdir()
    for i, (key, f) in enumerate(sorted(files.items())):
        data = f.read_bytes()
        (root / f"a{i}.safetensors").write_bytes(data if i else b"\x09" + data[1:])   # first one changed
    with pytest.raises(SystemExit, match=r"cleaned/seed1: no file .* with SHA-256"):
        testpass.locate(root, expected)


def test_a_duplicated_adapter_stops_the_job(tmp_path):
    expected, files = fake_expected(tmp_path)
    root = tmp_path / "input"
    root.mkdir()
    for i, (key, f) in enumerate(sorted(files.items())):
        (root / f"a{i}.safetensors").write_bytes(f.read_bytes())
    (root / "copy.safetensors").write_bytes(files[("cleaned", 2)].read_bytes())
    with pytest.raises(SystemExit, match="cleaned/seed2: 2 copies"):
        testpass.locate(root, expected)


def test_assembled_adapter_has_the_located_weights_and_the_committed_config(tmp_path):
    expected, files = fake_expected(tmp_path)
    root = tmp_path / "input"
    root.mkdir()
    for i, (key, f) in enumerate(sorted(files.items())):
        (root / f"a{i}.safetensors").write_bytes(f.read_bytes())
    d, src = testpass.assemble("cleaned", 2, root, tmp_path / "work", expected)
    assert sorted(p.name for p in d.iterdir()) == sorted(mainruns.ADAPTER_FILES)
    assert sha256(d / "adapter_model.safetensors") == expected[("cleaned", 2)]["sha256"]
    assert json.loads((d / "adapter_config.json").read_text()) == {"r": 16, "k": 2}


def dev_rows(path, flip=0):
    """Rows of a committed dev.csv, with the first `flip` right items turned wrong (reply kept)."""
    with open(path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        if flip and r["exe_correct"] == "1":
            r["exe_correct"], flip = "0", flip - 1
    return rows


def test_dev_check_tolerance_is_decision_38():
    committed = testpass.expected_adapters()[("cleaned", 1)]["dev_csv"]
    same = testpass.compare_replies(dev_rows(committed), committed)
    assert (same["same_reply"], same["discordant"], same["exe_correct_now"]) == (883, 0, 588)
    assert testpass.within_tolerance(same) is True
    assert testpass.within_tolerance(testpass.compare_replies(dev_rows(committed, flip=20), committed)) is True
    assert testpass.within_tolerance(testpass.compare_replies(dev_rows(committed, flip=21), committed)) is False
    assert testpass.within_tolerance({**same, "items": 3}) is None   # partial runs are not judged
    with pytest.raises(ValueError, match="different items"):
        testpass.compare_replies(dev_rows(committed)[:-1], committed)


def test_a_test_pass_stops_at_the_closed_gate_before_any_work(tmp_path, monkeypatch):
    """A closed gate stops a test pass before any work: no Hub call, no adapter copy, no model load.
    The real gate is pointed at a folder that is no git checkout, so it is closed whatever this repo's
    own gate says (it opened in S7, when check3 was committed)."""
    pytest.importorskip("torch")
    real = testgate.open_gate
    (tmp_path / "no-repo").mkdir()
    monkeypatch.setattr(testgate, "open_gate", lambda root=None: real(tmp_path / "no-repo"))
    called = []
    monkeypatch.setattr(testpass, "hub_main_sha", lambda m: called.append("hub"))
    monkeypatch.setattr(testpass, "assemble", lambda *a, **k: called.append("assemble"))
    with pytest.raises(testgate.GateClosed):
        testpass.run_pass("adapter:cleaned:1", tmp_path, tmp_path / "out", tmp_path / "work")
    assert called == [] and not (tmp_path / "out").exists()


def test_dev_check_and_test_pass_on_a_tiny_adapter(tmp_path, monkeypatch):
    """CPU: train one tiny main run, hide its adapter under another name, dev-check it, then run its
    test pass with the gate opened by a stand-in (the real gate is tested in test_testgate.py)."""
    pytest.importorskip("torch")
    pytest.importorskip("trl")
    from finqa_lora import tiny
    model = str(tiny.build(tmp_path / "tiny"))
    pilot_rep = tmp_path / "pilot" / "report.json"
    pilot_rep.parent.mkdir()
    pilot_rep.write_text(json.dumps({"written": "x", "prompt_fingerprint": None, "missing_runs": [],
                                     "chosen": {"lr": 1e-4, "epoch": 2, "mean_exe_correct": 0.0,
                                                "from_complete_pair": True}}))
    main = tmp_path / "results" / "main" / "run1"
    res = mainruns.run_one("cleaned", 1, main, model=model, dev_limit=3, report_path=pilot_rep,
                           subset=16, batch_size=4, grad_accum=1, epochs=3)
    d = main / "cleaned" / "seed1"
    expected = {("cleaned", 1): {"sha256": res["adapter_sha256"], "bytes": res["adapter_bytes"], "run": "run1",
                                 "folder": d, "config": d / "adapter" / "adapter_config.json",
                                 "dev_csv": d / "dev.csv"}}
    inp = tmp_path / "input" / "ds"
    inp.mkdir(parents=True)
    (inp / "x.safetensors").write_bytes((d / "adapter" / "adapter_model.safetensors").read_bytes())

    out = tmp_path / "out"
    check = testpass.devcheck(0, tmp_path / "input", out, tmp_path / "work", model_name=model, limit=3,
                              expected=expected)
    assert check["comparison"]["same_reply"] == 3 and check["within_tolerance"] is None
    assert check["adapter_source"].endswith("x.safetensors")

    record = {"check2": {"rows": 98}, "check3": {"rows": 50}}
    monkeypatch.setattr(testgate, "open_gate", lambda root=None: record)
    r = testpass.run_pass("adapter:cleaned:1", tmp_path / "input", out, tmp_path / "work", limit=3,
                          model_override=model, expected=expected)
    assert (r["test"]["items"], r["test"]["split"], r["test"]["test_gate"]) == (3, "test", record)
    assert r["adapter_sha256"] == res["adapter_sha256"] and r["revision"] is None
    assert (out / "cleaned" / "seed1" / "test.csv").read_text().count("\n") == 4
    rep = testpass.report(out)
    assert rep["one_gate_record"] and "adapter:cleaned:1" not in rep["missing_passes"]
    assert len(rep["missing_passes"]) == 12 and rep["test"]["adapter:cleaned:1"]["items"] == 3
