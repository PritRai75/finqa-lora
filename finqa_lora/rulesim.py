"""Simulation behind decision 39: how often does each winner rule declare a winner between identical arms?

A model of test-set correctness for two arms with S seeds each over 1,147 items:
  * item difficulty: logit ~ Normal(0.41 * spread, spread), so about 66% of items are right (as on dev)
    and most items are right or wrong in every run, as in the pilot;
  * training noise: each run adds one shift ~ Normal(0, run_shift) to every item's logit, which moves the
    whole run up or down (the pattern behind the pilot's same-seed McNemar p = 0.039);
  * a real effect: cleaning makes `effect_items` fixed, otherwise hard items right in every cleaned run.
spread 30 gives about 27 items right in one of two runs only when run_shift is 0 (same-seed level on
test); run_shift 0.5 and 1.0 give seed-to-seed accuracy spreads of about 0.65 and 1.2 points.

Three rules, each with the sign check over seed pairs:
  item_only            95% item bootstrap of the seed-averaged difference (the rule before decision 39)
  two_level            95% bootstrap over seeds within each arm, then items
  variance_components  difference +- t * sqrt(item variance + seed variance) (the rule from decision 39)

Usage: python -m finqa_lora.rulesim   (about 10 minutes; writes results/simulations/winner_rule.json)
"""
import json
import time

import numpy as np

from finqa_lora import REPO_ROOT, stats

OUT = REPO_ROOT / "results" / "simulations" / "winner_rule.json"
ITEMS = 1147
SCENARIOS = [(30, 0.0), (30, 0.5), (30, 1.0), (14, 0.5)]   # (item spread, run shift)
EFFECT_ITEMS = 23                                        # 23 of 1,147 items = +2.0 points
SIMS = 300
RESAMPLES = 1000
SEED = 20261119
RULES = ("item_only", "two_level", "variance_components")


def decide(cleaned, random, resamples, seed):
    """Which rules declare a winner (in either direction) for one simulated experiment."""
    pairs = np.mean(cleaned, axis=1) - np.mean(random, axis=1)
    same_sign = bool(np.all(pairs > 0) or np.all(pairs < 0))
    intervals = {
        "item_only": stats.paired_bootstrap(cleaned, random, resamples=resamples, seed=seed),
        "two_level": stats.two_level_bootstrap(cleaned, random, resamples=resamples, seed=seed),
        "variance_components": stats.variance_components(cleaned, random),
    }
    return {k: same_sign and (v["low"] > 0 or v["high"] < 0) for k, v in intervals.items()}


def simulate(spread, run_shift, effect_items, seeds, sims=SIMS, resamples=RESAMPLES, seed=SEED):
    rng = np.random.default_rng([seed, int(spread * 10), int(run_shift * 10), effect_items, seeds])
    base = rng.normal(0.41 * spread, spread, ITEMS)
    helped = rng.choice(np.flatnonzero(base < -3), effect_items, replace=False)

    def run(cleaned):
        x = (rng.random(ITEMS) < 1 / (1 + np.exp(-(base + rng.normal(0, run_shift))))).astype(np.int8)
        if cleaned:
            x[helped] = 1
        return x

    wins = dict.fromkeys(RULES, 0)
    seed_sd, discordant = [], []
    for k in range(sims):
        c = np.array([run(True) for _ in range(seeds)])
        r = np.array([run(False) for _ in range(seeds)])
        seed_sd.append(float(r.mean(axis=1).std(ddof=1)))
        discordant.append(int((r[0] != r[1]).sum()))
        for rule, won in decide(c, r, resamples, seed + k).items():
            wins[rule] += won
    return {"spread": spread, "run_shift": run_shift, "effect_items": effect_items, "seeds": seeds, "sims": sims,
            "mean_seed_sd_points": round(100 * float(np.mean(seed_sd)), 3),
            "mean_discordant_between_two_runs": round(float(np.mean(discordant)), 1),
            "winner_rate": {k: v / sims for k, v in wins.items()}}


def main():
    t0 = time.time()
    rows = []
    for spread, run_shift in SCENARIOS:
        for seeds in (3, 5):
            for effect in (0, EFFECT_ITEMS):
                row = simulate(spread, run_shift, effect, seeds)
                rows.append(row)
                label = "false winner" if effect == 0 else "power +2 pt"
                print(f"spread {spread} shift {run_shift} seeds {seeds} seed sd {row['mean_seed_sd_points']:.2f} pt  "
                      f"{label}: " + "  ".join(f"{k} {v:.1%}" for k, v in row["winner_rate"].items()), flush=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"written": time.strftime("%Y-%m-%d %H:%M:%S"), "numpy": np.__version__, "items": ITEMS,
                   "sims": SIMS, "resamples": RESAMPLES, "seed": SEED, "effect_items": EFFECT_ITEMS,
                   "seconds": round(time.time() - t0, 1), "rows": rows}, f, indent=2)
        f.write("\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
