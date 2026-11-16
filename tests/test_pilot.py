"""The pilot's selection rule, folder names and noise report; a full run on a tiny model (CPU)."""
import json

import pytest

from finqa_lora import pilot


@pytest.mark.parametrize("lr, name", [(1e-4, "lr1e-4"), (2e-4, "lr2e-4"), (5e-5, "lr5e-5"), (1e-3, "lr1e-3")])
def test_lr_names(lr, name):
    assert pilot.lr_name(lr) == name


def test_checkpoints_sort_by_step_not_text(tmp_path):
    for step in (364, 1092, 728, 99):
        (tmp_path / f"checkpoint-{step}").mkdir()
    (tmp_path / "checkpoint-final").mkdir()
    assert [p.name for p in pilot.epoch_checkpoints(tmp_path)] == [
        "checkpoint-99", "checkpoint-364", "checkpoint-728", "checkpoint-1092"]


def result(lr, rep, *exe_correct):
    return {"lr": lr, "rep": rep, "epochs": [{"epoch": i, "exe_correct": c} for i, c in enumerate(exe_correct, 1)]}


def test_rule_uses_the_mean_of_runs_a_and_b():
    # Run a alone would pick 2e-4 epoch 3 (510); averaged with run b, 1e-4 epoch 2 is higher.
    rs = [result(1e-4, "a", 480, 500, 499), result(1e-4, "b", 482, 504, 498),
          result(2e-4, "a", 490, 495, 510), result(2e-4, "b", 488, 494, 490)]
    chosen, table = pilot.select(rs)
    assert chosen == {"lr": 1e-4, "epoch": 2, "mean_exe_correct": 502.0, "from_complete_pair": True}
    assert len(table) == 6 and all(r["complete"] for r in table)


def test_ties_go_to_fewer_epochs_then_lower_lr():
    rs = [result(1e-4, "a", 400, 500), result(1e-4, "b", 400, 500),
          result(2e-4, "a", 500, 500), result(2e-4, "b", 500, 500)]
    assert pilot.select(rs)[0]["lr"] == 2e-4 and pilot.select(rs)[0]["epoch"] == 1
    rs = [result(2e-4, "a", 500), result(2e-4, "b", 500), result(1e-4, "a", 500), result(1e-4, "b", 500)]
    assert pilot.select(rs)[0] == {"lr": 1e-4, "epoch": 1, "mean_exe_correct": 500.0, "from_complete_pair": True}


def test_a_missing_run_is_flagged_not_hidden():
    chosen, table = pilot.select([result(1e-4, "a", 500), result(2e-4, "a", 400), result(2e-4, "b", 410)])
    assert chosen["from_complete_pair"] is False
    assert [r["complete"] for r in table] == [False, True]
    assert pilot.select([]) == (None, [])


def test_rule_is_written_down_before_results():
    assert "averaged over runs a and b" in pilot.RULE and "fewer epochs" in pilot.RULE
    assert pilot.LEARNING_RATES == (1e-4, 2e-4) and pilot.SEED == 1
    assert pilot.MODEL == "Qwen/Qwen2.5-1.5B-Instruct"


def test_full_pilot_on_tiny_model(tmp_path):
    pytest.importorskip("torch")
    pytest.importorskip("trl")
    from finqa_lora import tiny
    model = str(tiny.build(tmp_path / "tiny"))
    out = tmp_path / "pilot"
    for lr in pilot.LEARNING_RATES:
        for rep in pilot.REPS:
            pilot.run_one(lr, rep, out, model=model, dev_limit=4, subset=16, epochs=2, batch_size=4,
                          grad_accum=1)
    rep = pilot.report(out)
    assert rep["missing_runs"] == [] and rep["chosen"]["from_complete_pair"]
    assert json.loads((out / "report.json").read_text()) == rep
    run = out / "lr1e-4" / "a"
    assert sorted(p.name for p in run.glob("dev_epoch*.csv")) == ["dev_epoch1.csv", "dev_epoch2.csv"]
    res = json.loads((run / "result.json").read_text())
    assert [e["step"] for e in res["epochs"]] == [4, 8]
    assert all(len(e["adapter_sha256"]) == 64 for e in res["epochs"])
    assert res["train"]["config"]["sampling"] == "group_by_length"
    # Weights pruned after scoring; loss logs kept.
    assert not list(out.rglob("adapter_model.safetensors")) and not list(out.rglob("tokenizer.json"))
    assert len(list(run.glob("train/checkpoint-*/trainer_state.json"))) == 2
    # CPU training is deterministic, so a same-seed retrain repeats exactly here. On a GPU it may not.
    assert all(n["same_adapter"] and n["same_reply"] == n["items"] for n in rep["same_seed_noise"]["dev"])
    assert all(t["same_logged_losses"] for t in rep["same_seed_noise"]["training"])
