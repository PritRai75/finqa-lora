"""The run log is built from committed results and agrees with every report it reads."""
import csv
import json
import shutil

import pytest

from finqa_lora import runlog
from finqa_lora.data import load_split

DEV_IDS = [ex["id"] for ex in load_split("dev")]
FIELDS = ["id", "reply", "program", "executes", "value", "exe_correct", "prog_correct"]


@pytest.fixture
def results(tmp_path):
    """A results tree holding the committed feasibility run 1 and a small fake pilot run."""
    root = tmp_path / "results"
    shutil.copytree(runlog.RESULTS / "feasibility" / "run1", root / "feasibility" / "run1")
    pilot = root / "pilot" / "run1"
    (pilot).mkdir(parents=True)
    (pilot / "report.json").write_text(json.dumps({"prompt_version": 1, "prompt_fingerprint": "4139bfc3519c"}))
    for lr, name in ((1e-4, "lr1e-4"), (2e-4, "lr2e-4")):
        for rep in ("a", "b"):
            fake_pilot_run(pilot / name / rep, lr, rep, right={0: [0, 5], 1: [0, 5, 9]})
    return root


def fake_pilot_run(folder, lr, rep, right, ids=DEV_IDS, recorded_offset=0):
    folder.mkdir(parents=True)
    epochs = []
    for k, right_positions in right.items():
        with open(folder / f"dev_epoch{k + 1}.csv", "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
            w.writeheader()
            for i, item in enumerate(reversed(ids)):          # out of split order on purpose
                ok = int(len(ids) - 1 - i in right_positions)
                w.writerow({"id": item, "reply": "add(1, 2)", "program": "add(1, 2)", "executes": 1,
                            "value": 3.0, "exe_correct": ok, "prog_correct": 0})
        epochs.append({"epoch": k + 1, "step": 364 * (k + 1), "adapter_sha256": f"{lr}{rep}{k}".ljust(64, "0"),
                       "items": len(ids), "exe_correct": len(right_positions) + recorded_offset,
                       "prog_correct": 0, "executes": len(ids)})
    config = {"model": "Qwen/Qwen2.5-1.5B-Instruct", "arm": "cleaned", "seed": 1, "learning_rate": lr,
              "out": f"/kaggle/working/pilot/{rep}/train"}          # out differs between a and b
    (folder / "result.json").write_text(json.dumps({
        "lr": lr, "rep": rep, "gpu": "Tesla T4", "epochs": epochs,
        "train": {"config": config, "git_commit": "0430491"}}))


def test_feasibility_runs_match_their_report(results, tmp_path):
    counts = runlog.build(db=tmp_path / "runs.db", results=results)
    assert counts == {"feasibility/run1": 6, "pilot/run1": 8}
    con = runlog.connect(tmp_path / "runs.db")
    got = {r["run_id"]: r["exe_correct"] for r in con.execute("SELECT * FROM runs WHERE kind = 'base'")}
    assert got == {  # feasibility run 1, report.json (10 Nov 2026)
        "feasibility/run1/Qwen/Qwen2.5-1.5B-Instruct/dev_base_0shot": 29,
        "feasibility/run1/Qwen/Qwen2.5-1.5B-Instruct/dev_base_4shot": 43,
        "feasibility/run1/Qwen/Qwen2.5-1.5B-Instruct/dev_base_0shot_repeat": 29,
        "feasibility/run1/Qwen/Qwen3-4B-Instruct-2507/dev_base_0shot": 224,
        "feasibility/run1/Qwen/Qwen3-4B-Instruct-2507/dev_base_4shot": 221,
        "feasibility/run1/Qwen/Qwen3-4B-Instruct-2507/dev_base_0shot_repeat": 224,
    }
    row = con.execute("SELECT * FROM runs WHERE run_id LIKE '%2.5-1.5B%0shot'").fetchone()
    assert (row["git_commit"][:7], row["prompt_fingerprint"], row["gpu"]) == ("59f8396", "4139bfc3519c", "Tesla T4")
    assert row["csv_path"] == "results/feasibility/run1/Qwen__Qwen2.5-1.5B-Instruct/dev_base_0shot.csv"
    # Greedy decoding repeated exactly in run 1, so the two vectors are equal item for item.
    first = runlog.vector(con, "feasibility/run1/Qwen/Qwen2.5-1.5B-Instruct/dev_base_0shot")
    assert first == runlog.vector(con, "feasibility/run1/Qwen/Qwen2.5-1.5B-Instruct/dev_base_0shot_repeat")
    assert len(first) == 883 and sum(first) == 29


def test_pilot_rows_carry_adapter_and_config(results, tmp_path):
    runlog.build(db=tmp_path / "runs.db", results=results)
    con = runlog.connect(tmp_path / "runs.db")
    rows = {r["run_id"]: r for r in con.execute("SELECT * FROM runs WHERE kind = 'finetuned'")}
    a, b = rows["pilot/run1/lr1e-4/a/epoch2"], rows["pilot/run1/lr1e-4/b/epoch2"]
    assert (a["lr"], a["epoch"], a["step"], a["seed"], a["arm"]) == (1e-4, 2, 728, 1, "cleaned")
    assert a["config_hash"] == b["config_hash"] != rows["pilot/run1/lr2e-4/a/epoch2"]["config_hash"]
    assert "out" not in json.loads(a["config_json"])
    assert a["adapter_sha256"] != b["adapter_sha256"]


def test_vector_follows_split_order(results, tmp_path):
    runlog.build(db=tmp_path / "runs.db", results=results)
    con = runlog.connect(tmp_path / "runs.db")
    v = runlog.vector(con, "pilot/run1/lr1e-4/a/epoch2")
    assert [i for i, x in enumerate(v) if x] == [0, 5, 9]
    with pytest.raises(KeyError):
        runlog.vector(con, "pilot/run1/lr5e-4/a/epoch1")


def test_partial_runs_are_logged_but_refused_for_statistics(tmp_path):
    root = tmp_path / "results"
    (root / "pilot" / "run1").mkdir(parents=True)
    (root / "pilot" / "run1" / "report.json").write_text("{}")
    fake_pilot_run(root / "pilot" / "run1" / "lr1e-4" / "a", 1e-4, "a", {0: [1]}, ids=DEV_IDS[:6])
    runlog.build(db=tmp_path / "runs.db", results=root)
    con = runlog.connect(tmp_path / "runs.db")
    with pytest.raises(ValueError, match="covers 6 of 883"):
        runlog.vector(con, "pilot/run1/lr1e-4/a/epoch1")


@pytest.mark.parametrize("break_it, message", [
    (lambda f: fake_pilot_run(f, 1e-4, "a", {0: [1]}, recorded_offset=1), "its report recorded"),
    (lambda f: fake_pilot_run(f, 1e-4, "a", {0: [1]}, ids=DEV_IDS[:5] + ["NOT/AN/ITEM"]), "is not in dev"),
    (lambda f: fake_pilot_run(f, 1e-4, "a", {0: [1]}, ids=DEV_IDS[:5] + DEV_IDS[:1]), "appears twice"),
])
def test_bad_results_stop_the_build_and_keep_the_old_db(tmp_path, break_it, message):
    root = tmp_path / "results"
    (root / "pilot" / "run1").mkdir(parents=True)
    (root / "pilot" / "run1" / "report.json").write_text("{}")
    db = tmp_path / "runs.db"
    db.write_text("previous build")
    break_it(root / "pilot" / "run1" / "lr1e-4" / "a")
    with pytest.raises(ValueError, match=message):
        runlog.build(db=db, results=root)
    assert db.read_text() == "previous build"


def test_the_repo_results_build(tmp_path):
    """Whatever is committed under results/ must always build."""
    counts = runlog.build(db=tmp_path / "runs.db")
    assert counts["feasibility/run1"] == 6
    assert counts["pilot/run1"] == 12   # 2 learning rates x runs a, b x 3 epochs (Kaggle, 16 Nov 2026)
    assert counts["main/run1"] == 6     # seeds 1 to 3 x 2 arms (Kaggle, 19 Nov 2026)
    assert counts["main/run2"] == 4     # seeds 4 and 5 x 2 arms (Kaggle, 19 Nov 2026)
    con = runlog.connect(tmp_path / "runs.db")
    assert sum(runlog.vector(con, "pilot/run1/lr2e-4/a/epoch3")) == 589
    assert sum(runlog.vector(con, "main/run1/cleaned/seed1/dev")) == 588
    assert sum(runlog.vector(con, "main/run2/cleaned/seed5/dev")) == 596


def fake_main_run(folder, arm, seed, right, ids=DEV_IDS):
    folder.mkdir(parents=True)
    with open(folder / "dev.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        for i, item in enumerate(ids):
            w.writerow({"id": item, "reply": "add(1, 2)", "program": "add(1, 2)", "executes": 1, "value": 3.0,
                        "exe_correct": int(i in right), "prog_correct": 0})
    config = {"model": "Qwen/Qwen2.5-1.5B-Instruct", "arm": arm, "seed": seed, "learning_rate": 1e-4,
              "stop_after_epoch": 2, "out": f"/kaggle/working/main/{arm}/seed{seed}/train"}
    (folder / "result.json").write_text(json.dumps({
        "arm": arm, "seed": seed, "lr": 1e-4, "epoch": 2, "step": 728, "gpu": "Tesla T4",
        "adapter_sha256": f"{arm}{seed}".ljust(64, "0"),
        "dev": {"items": len(ids), "exe_correct": len(right), "prog_correct": 0, "executes": len(ids)},
        "train": {"config": config, "git_commit": "abc1234", "prompt_version": 1,
                  "prompt_fingerprint": "4139bfc3519c"}}))


def test_main_runs_are_read_with_arm_and_seed(tmp_path):
    root = tmp_path / "results" / "main" / "run1"
    for arm, seed, right in (("cleaned", 1, [0, 3]), ("random", 1, [3])):
        fake_main_run(root / arm / f"seed{seed}", arm, seed, right)
    (root / "report.json").write_text(json.dumps({"runs": [{}, {}]}))
    assert runlog.build(db=tmp_path / "runs.db", results=tmp_path / "results") == {"main/run1": 2}
    con = runlog.connect(tmp_path / "runs.db")
    row = con.execute("SELECT * FROM runs WHERE run_id = 'main/run1/cleaned/seed1/dev'").fetchone()
    assert (row["arm"], row["seed"], row["epoch"], row["step"], row["prompt_fingerprint"]) == (
        "cleaned", 1, 2, 728, "4139bfc3519c")
    cleaned, rand = (runlog.vector(con, f"main/run1/{a}/seed1/dev") for a in ("cleaned", "random"))
    assert [i for i, x in enumerate(cleaned) if x] == [0, 3] and sum(rand) == 1
    a, b = (con.execute(f"SELECT config_hash FROM runs WHERE arm = '{a}'").fetchone()[0] for a in ("cleaned", "random"))
    assert a != b   # the arm is part of the config


def test_main_run_missing_from_its_report_stops_the_build(tmp_path):
    root = tmp_path / "results" / "main" / "run1"
    fake_main_run(root / "cleaned" / "seed1", "cleaned", 1, [0])
    (root / "report.json").write_text(json.dumps({"runs": []}))
    with pytest.raises(ValueError, match="1 result.json files, its report lists 0 runs"):
        runlog.build(db=tmp_path / "runs.db", results=tmp_path / "results")
