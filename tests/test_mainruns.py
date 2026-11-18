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
    vs = rep["cleaned_seed1_vs_pilot"]
    assert vs["a"]["same_adapter"] and vs["b"]["same_adapter"]
    assert (vs["a"]["same_reply"], vs["a"]["discordant"], vs["a"]["within_tolerance"]) == (3, 0, None)  # 3 of 883 items


PILOT = REPO_ROOT / "results" / "pilot" / "run1"


def test_frozen_config_is_the_pilot_choice():
    """Decision 37 (S4): the committed pilot chose lr 2e-4 at epoch 3 (dev 589 and 582, mean 585.5)."""
    fz = mainruns.frozen()
    assert (fz["lr"], fz["epoch"], fz["pilot_mean_dev_exe_correct"]) == (2e-4, 3, 585.5)
    assert fz["pilot_report"] == "results/pilot/run1/report.json" and fz["prompt_fingerprint"] == "4139bfc3519c"


def test_repeat_tolerance_holds_for_every_pilot_pair():
    """Decision 38: the tolerance was set from these six same-seed pairs; each must pass it."""
    seen = []
    for lr in ("lr1e-4", "lr2e-4"):
        for e in (1, 2, 3):
            c = mainruns.compare_dev(PILOT / lr / "a" / f"dev_epoch{e}.csv", PILOT / lr / "b" / f"dev_epoch{e}.csv")
            assert c["within_tolerance"], (lr, e, c)
            seen.append((c["same_reply"], c["discordant"]))
    assert min(s for s, _ in seen) == 833 and max(s for s, _ in seen) == 863
    assert min(d for _, d in seen) == 3 and max(d for _, d in seen) == 13


def test_repeat_tolerance_flags_a_run_that_changed(tmp_path):
    """21 items flipped from right to wrong against the pilot's run a: outside the tolerance."""
    import csv
    src = PILOT / "lr2e-4" / "a" / "dev_epoch3.csv"
    with open(src, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    flipped = 0
    for r in rows:
        if r["exe_correct"] == "1" and flipped < 21:
            r["exe_correct"], flipped = "0", flipped + 1
    changed = tmp_path / "dev.csv"
    with open(changed, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    c = mainruns.compare_dev(changed, src)
    assert (c["same_reply"], c["right_in_pilot_only"], c["within_tolerance"]) == (883, 21, False)
