"""Decision 39's evidence: the committed simulation, its code, and the same-seed pilot pairs behind it."""
import csv
import json

import pytest

from finqa_lora import REPO_ROOT, rulesim, stats
from finqa_lora.data import load_split

SIM = json.loads(rulesim.OUT.read_text(encoding="utf-8"))
PILOT = REPO_ROOT / "results" / "pilot" / "run1"
DEV_IDS = [ex["id"] for ex in load_split("dev")]


def test_committed_simulation_came_from_this_code():
    assert (SIM["sims"], SIM["resamples"], SIM["seed"], SIM["effect_items"], SIM["items"]) == (
        rulesim.SIMS, rulesim.RESAMPLES, rulesim.SEED, rulesim.EFFECT_ITEMS, rulesim.ITEMS)
    got = {(r["spread"], r["run_shift"], r["seeds"], r["effect_items"]) for r in SIM["rows"]}
    assert got == {(sp, sh, s, e) for sp, sh in rulesim.SCENARIOS for s in (3, 5) for e in (0, rulesim.EFFECT_ITEMS)}


def test_short_rerun_is_exact():
    """The first 40 simulations of the spread 30, shift 1.0, 3-seed null row (numpy 2.5.3, pinned)."""
    row = rulesim.simulate(30, 1.0, 0, 3, sims=40)
    assert row["winner_rate"] == {"item_only": 8 / 40, "two_level": 6 / 40, "variance_components": 2 / 40}


def test_the_rule_stays_calibrated_and_the_old_one_did_not():
    for r in SIM["rows"]:
        rate = r["winner_rate"]
        if r["effect_items"] == 0:
            assert rate["variance_components"] <= 0.05, r          # never more than 5% false winners
            if r["seeds"] == 3 and r["run_shift"] > 0:
                assert rate["item_only"] >= 0.15, r                # the pre-decision-39 rule, 3 seeds
    def power(spread, shift, seeds):
        return next(r["winner_rate"]["variance_components"] for r in SIM["rows"] if r["effect_items"]
                    and (r["spread"], r["run_shift"], r["seeds"]) == (spread, shift, seeds))
    assert power(30, 0.5, 5) > power(30, 0.5, 3) + 0.25                # decision 40: 5 seeds buy power


def dev_vector(path):
    with open(path, encoding="utf-8", newline="") as f:
        right = {r["id"]: int(r["exe_correct"]) for r in csv.DictReader(f)}
    return [right[i] for i in DEV_IDS]


@pytest.mark.parametrize("lr, epoch, excludes_zero", [("lr2e-4", 3, True), ("lr1e-4", 1, True), ("lr2e-4", 2, False)])
def test_item_only_interval_on_same_seed_pilot_pairs(lr, epoch, excludes_zero):
    """Runs a and b share data, seed, batches and settings, yet the item-only interval excludes zero twice."""
    a, b = (dev_vector(PILOT / lr / rep / f"dev_epoch{epoch}.csv") for rep in "ab")
    out = stats.paired_bootstrap([a], [b])
    assert (out["low"] > 0 or out["high"] < 0) is excludes_zero
