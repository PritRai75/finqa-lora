"""Main runs: the frozen config comes only from a complete pilot, the job file matches the plan, and a
run stopped at the chosen epoch is the same training as the pilot's run up to that epoch (CPU)."""
import json
import re

import pytest

from finqa_lora import REPO_ROOT, mainruns, pilot


def write_report(path, chosen=None, missing=()):
    chosen = chosen or {"lr": 1e-4, "epoch": 2, "mean_exe_correct": 3.0, "from_complete_pair": True}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"written": "x", "prompt_fingerprint": None, "missing_runs": list(missing),
                                "chosen": chosen}), encoding="utf-8")
    return path


def test_plan_is_three_seeds_of_both_arms_paired_by_slot():
    assert mainruns.ARMS == ("cleaned", "random") and mainruns.SEEDS == (1, 2, 3)
    assert mainruns.SCHEDULE_EPOCHS == 3.0 and mainruns.MODEL == "Qwen/Qwen2.5-1.5B-Instruct"
    runs = [r for chain in mainruns.CHAINS.values() for r in chain]
    assert sorted(runs) == sorted((a, s) for a in mainruns.ARMS for s in mainruns.SEEDS)
    for slot in zip(*mainruns.CHAINS.values()):
        assert {a for a, _ in slot} == set(mainruns.ARMS) and len({s for _, s in slot}) == 1


def test_job_file_runs_the_chains_in_the_module():
    text = (REPO_ROOT / "jobs" / "main.sh").read_text(encoding="utf-8")
    found = {int(g): [(a, int(s)) for a, s in re.findall(r"(\w+):(\d)", jobs)]
             for g, jobs in re.findall(r"^chain (\d) ((?:\w+:\d ?)+)", text, re.M)}
    assert found == mainruns.CHAINS


def test_frozen_reads_the_chosen_lr_and_epoch(tmp_path):
    fz = mainruns.frozen(write_report(tmp_path / "report.json"))
    assert (fz["lr"], fz["epoch"]) == (1e-4, 2)


@pytest.mark.parametrize("kwargs", [dict(missing=["lr2e-4/b"]),
                                    dict(chosen={"lr": 1e-4, "epoch": 1, "mean_exe_correct": 1.0,
                                                 "from_complete_pair": False})])
def test_frozen_refuses_an_incomplete_pilot(tmp_path, kwargs):
    with pytest.raises(SystemExit, match="incomplete"):
        mainruns.frozen(write_report(tmp_path / "report.json", **kwargs))


def test_frozen_refuses_a_missing_pilot(tmp_path):
    with pytest.raises(SystemExit, match="commit the pilot record"):
        mainruns.frozen(tmp_path / "nope.json")


def test_stopped_run_repeats_the_pilot_up_to_the_chosen_epoch(tmp_path):
    """Pilot (3 epochs, seed 1, cleaned) and main run (stopped after epoch 2) on the tiny model, CPU.

    CPU training repeats bit for bit, so the main run's adapter must equal the pilot's epoch-2
    adapter: the stop changed nothing before it, the schedule included.
    """
    pytest.importorskip("torch")
    pytest.importorskip("trl")
    from finqa_lora import tiny
    model = str(tiny.build(tmp_path / "tiny"))
    small = dict(subset=16, batch_size=4, grad_accum=1)
    p_out = tmp_path / "results" / "pilot" / "run1"
    for rep in pilot.REPS:
        pilot.run_one(1e-4, rep, p_out, model=model, dev_limit=3, epochs=3, **small)
    report = write_report(p_out / "report.json")

    out = tmp_path / "main"
    res = mainruns.run_one("cleaned", 1, out, model=model, dev_limit=3, report_path=report, epochs=3, **small)
    pilot_a = json.loads((p_out / "lr1e-4" / "a" / "result.json").read_text())
    assert res["step"] == pilot_a["epochs"][1]["step"] == 8
    assert res["adapter_sha256"] == pilot_a["epochs"][1]["adapter_sha256"]
    assert res["final_is_chosen_epoch"]   # the adapter saved at the stop is the epoch-2 checkpoint

    d = out / "cleaned" / "seed1"
    assert sorted(p.name for p in (d / "adapter").iterdir()) == sorted(mainruns.ADAPTER_FILES)
    assert [p.relative_to(d).as_posix() for p in d.rglob("*.safetensors")] == ["adapter/adapter_model.safetensors"]
    assert not list(d.rglob("tokenizer.json"))
    assert (d / "dev.csv").read_text().count("\n") == 4 and res["dev"]["items"] == 3

    rep = mainruns.report(out, report)
    assert rep["complete_seed_pairs"] == [] and "random/seed1" in rep["missing_runs"]
    assert rep["cleaned_seed1_vs_pilot"]["a"]["same_adapter"] and rep["cleaned_seed1_vs_pilot"]["b"]["same_adapter"]
