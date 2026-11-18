"""Statistics for the results: intervals, paired tests and the winner rule fixed in the spec.

Everything works on per-item 0/1 correctness vectors over the same items in the same order
(1,147 test items, or 883 dev items). numpy only; tests check each function against scipy and
statsmodels where those are installed, and against pinned reference values everywhere else.

  wilson(k, n)                       95% Wilson score interval for one accuracy
  mcnemar_exact(a, b)                exact two-sided McNemar test for two models on the same items
  paired_bootstrap(cleaned, random)  seed-averaged difference, percentile interval over items only
  two_level_bootstrap(cleaned, random)  the same, resampling seeds within each arm and then items
  variance_components(cleaned, random)  the same difference, interval from item and seed variance with
                                        a t quantile: the interval the winner rule uses (decision 39)
  winner(cleaned, random)            the rule fixed before any test-set number (spec, section 4)

Why the winner rule changed (decision 39, 19 Nov 2026, before any main-run result): training noise
moves a whole run up or down, which an item-only interval cannot see. Two same-seed pilot runs, with
identical data and batches, differ with an item-only interval that excludes zero in 2 of 3 cases
checked. In simulation (finqa_lora/rulesim.py, results/simulations/winner_rule.json) the item-only
rule declared a winner between identical arms in 21 to 29% of cases once seeds differ by 0.6 to 1.2
accuracy points; resampling only 3 seeds (two-level) still did in 11 to 17%; the variance-components
interval stayed at 4 to 6%.
"""
import math

import numpy as np

Z95 = 1.959963984540054          # standard normal 97.5% quantile
BOOTSTRAP_SEED = 20261116
BOOTSTRAP_RESAMPLES = 10_000
# Student t 97.5% quantiles by degrees of freedom, from scipy.stats.t.ppf (scipy 1.18.1); a test
# checks them against scipy when it is installed.
T975 = {1: 12.706204736175, 2: 4.302652729749, 3: 3.182446305284, 4: 2.776445105198, 5: 2.570581835636,
        6: 2.446911851145, 7: 2.364624251593, 8: 2.306004135204, 9: 2.262157162798, 10: 2.228138851986,
        11: 2.200985160092, 12: 2.178812829667}


def wilson(k, n, z=Z95):
    """Wilson score interval for k successes in n trials. Returns (low, high) as proportions."""
    if n <= 0:
        raise ValueError("n must be positive")
    if not 0 <= k <= n:
        raise ValueError("k must be between 0 and n")
    p = k / n
    denom = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return max(0.0, centre - half), min(1.0, centre + half)


def _vector(x, name):
    v = np.asarray(x)
    if v.ndim != 1 or not np.isin(v, (0, 1)).all():
        raise ValueError(f"{name} must be a 1-D vector of 0/1 per item")
    return v.astype(np.int8)


def discordant(a, b):
    """Items right in a only, and items right in b only."""
    a, b = _vector(a, "a"), _vector(b, "b")
    if a.shape != b.shape:
        raise ValueError("a and b must cover the same items")
    return int(((a == 1) & (b == 0)).sum()), int(((a == 0) & (b == 1)).sum())


def _binom_cdf_half(k, n):
    """P(X <= k) for X ~ Binomial(n, 1/2), exact with integers."""
    return sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n


def mcnemar_exact(a, b):
    """Exact two-sided McNemar test (binomial test on the discordant items).

    p = min(1, 2 * P(X <= min(n01, n10))), X ~ Binomial(n01 + n10, 1/2); p = 1 when there are no
    discordant items. Same as statsmodels' mcnemar(exact=True) and scipy's binomtest two-sided.
    """
    n10, n01 = discordant(a, b)
    n = n10 + n01
    p = 1.0 if n == 0 else min(1.0, 2 * _binom_cdf_half(min(n10, n01), n))
    return {"a_only": n10, "b_only": n01, "discordant": n, "p": p}


def _matrix(runs, name):
    m = np.vstack([_vector(r, f"{name} run") for r in runs])
    return m


def paired_bootstrap(cleaned, random, resamples=BOOTSTRAP_RESAMPLES, seed=BOOTSTRAP_SEED):
    """Seed-averaged accuracy difference, cleaned minus random, with a 95% percentile interval.

    cleaned and random are lists of per-item vectors, one per seed. Items are resampled with
    replacement and every run keeps its own answer on each resampled item, so the pairing of items
    across runs is kept and seed spread stays inside the statistic.
    """
    c, r = _matrix(cleaned, "cleaned"), _matrix(random, "random")
    if c.shape[1] != r.shape[1]:
        raise ValueError("all runs must cover the same items")
    per_item = c.mean(axis=0) - r.mean(axis=0)            # each item's seed-averaged difference
    n = per_item.size
    rng = np.random.default_rng(seed)
    stats = np.empty(resamples)
    for start in range(0, resamples, 1000):                # chunks keep memory small
        idx = rng.integers(0, n, size=(min(1000, resamples - start), n))
        stats[start:start + idx.shape[0]] = per_item[idx].mean(axis=1)
    low, high = np.percentile(stats, [2.5, 97.5])
    return {"difference": float(per_item.mean()), "low": float(low), "high": float(high),
            "items": int(n), "resamples": resamples, "seed": seed}


def two_level_bootstrap(cleaned, random, resamples=BOOTSTRAP_RESAMPLES, seed=BOOTSTRAP_SEED):
    """Seed-averaged difference with a percentile interval that resamples seeds, then items.

    Each resample draws as many seeds as each arm has, with replacement and separately per arm, and
    one set of items shared by both arms. Reported beside the rule's interval; with 3 seeds it is
    still too narrow (simulation, decision 39), because 3 seeds understate their own spread.
    """
    c, r = _matrix(cleaned, "cleaned"), _matrix(random, "random")
    if c.shape[1] != r.shape[1]:
        raise ValueError("all runs must cover the same items")
    (sc, n), sr = c.shape, r.shape[0]
    rng = np.random.default_rng(seed)
    out = np.empty(resamples)
    for start in range(0, resamples, 500):
        b = min(500, resamples - start)
        idx = rng.integers(0, n, size=(b, n))
        cm, rm = c[:, idx].mean(axis=-1), r[:, idx].mean(axis=-1)          # (seeds, b): each run on each resample
        kc, kr = rng.integers(0, sc, size=(b, sc)), rng.integers(0, sr, size=(b, sr))
        out[start:start + b] = (np.take_along_axis(cm.T, kc, 1).mean(1) - np.take_along_axis(rm.T, kr, 1).mean(1))
    low, high = np.percentile(out, [2.5, 97.5])
    return {"difference": float(c.mean() - r.mean()), "low": float(low), "high": float(high),
            "items": int(n), "seeds": [int(sc), int(sr)], "resamples": resamples, "seed": seed}


def variance_components(cleaned, random):
    """Seed-averaged difference, cleaned minus random, with the 95% interval the winner rule uses.

    se^2 = var(per-item seed-averaged difference) / items       (which items: item sampling)
         + s^2 * (1 / cleaned seeds + 1 / random seeds)          (which training runs: seed spread)
    where s^2 is the pooled within-arm variance of the runs' accuracies, with cleaned seeds + random
    seeds - 2 degrees of freedom, and the interval is difference +- t(97.5%, df) * se. The t quantile
    carries the uncertainty of estimating s^2 from a few seeds. Item-level noise enters both terms,
    so the interval is a little wide when runs barely differ (conservative, by design).
    """
    c, r = _matrix(cleaned, "cleaned"), _matrix(random, "random")
    if c.shape[1] != r.shape[1]:
        raise ValueError("all runs must cover the same items")
    sc, sr = c.shape[0], r.shape[0]
    if min(sc, sr) < 2:
        raise ValueError("the seed term needs at least 2 seeds per arm")
    per_item = c.mean(axis=0) - r.mean(axis=0)
    n = per_item.size
    se_item2 = float(per_item.var(ddof=1)) / n
    acc_c, acc_r = c.mean(axis=1), r.mean(axis=1)
    df = sc + sr - 2
    s2 = float(((sc - 1) * acc_c.var(ddof=1) + (sr - 1) * acc_r.var(ddof=1)) / df)
    se = math.sqrt(se_item2 + s2 * (1 / sc + 1 / sr))
    q = T975[df]
    diff = float(per_item.mean())
    return {"difference": diff, "low": diff - q * se, "high": diff + q * se, "se": se,
            "se_items": math.sqrt(se_item2), "seed_sd": math.sqrt(s2), "df": df, "t975": q,
            "items": int(n), "seeds": [int(sc), int(sr)]}


def winner(cleaned, random, **bootstrap_args):
    """The winner rule fixed before any test-set number exists (spec, section 4; decision 39).

    "Cleaning helped" (or "cleaning hurt") only if the 95% variance-components interval on the
    seed-averaged difference excludes zero AND every seed pair (cleaned seed s against random seed s)
    has a difference of that same sign. Otherwise: no detectable difference. The item-only and
    two-level bootstrap intervals are reported beside it and decide nothing.
    """
    if len(cleaned) != len(random):
        raise ValueError("each cleaned seed needs its random partner with the same seed")
    vc = variance_components(cleaned, random)
    pairs = [float(_vector(c, "cleaned").mean() - _vector(r, "random").mean()) for c, r in zip(cleaned, random)]
    if vc["low"] > 0 and all(d > 0 for d in pairs):
        verdict = "cleaning helped"
    elif vc["high"] < 0 and all(d < 0 for d in pairs):
        verdict = "cleaning hurt"
    else:
        verdict = "no detectable difference"
    return {"verdict": verdict, "rule": "variance_components", "seed_pair_differences": pairs, **vc,
            "item_bootstrap": paired_bootstrap(cleaned, random, **bootstrap_args),
            "two_level_bootstrap": two_level_bootstrap(cleaned, random, **bootstrap_args)}
