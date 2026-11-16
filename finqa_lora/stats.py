"""Statistics for the results: intervals, paired tests and the winner rule fixed in the spec.

Everything works on per-item 0/1 correctness vectors over the same items in the same order
(1,147 test items, or 883 dev items). numpy only; tests check each function against scipy and
statsmodels where those are installed, and against pinned reference values everywhere else.

  wilson(k, n)                       95% Wilson score interval for one accuracy
  mcnemar_exact(a, b)                exact two-sided McNemar test for two models on the same items
  paired_bootstrap(cleaned, random)  seed-averaged difference with a percentile interval over items
  winner(cleaned, random)            the rule fixed before any test-set number (spec, section 4)
"""
import math

import numpy as np

Z95 = 1.959963984540054          # standard normal 97.5% quantile
BOOTSTRAP_SEED = 20261116
BOOTSTRAP_RESAMPLES = 10_000


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


def winner(cleaned, random, **bootstrap_args):
    """The winner rule fixed before any test-set number exists (spec, section 4).

    "Cleaning helped" (or "cleaning hurt") only if the 95% paired-bootstrap interval on the
    seed-averaged difference excludes zero AND every seed pair (cleaned seed s against random
    seed s) has a difference of that same sign. Otherwise: no detectable difference.
    """
    if len(cleaned) != len(random):
        raise ValueError("each cleaned seed needs its random partner with the same seed")
    boot = paired_bootstrap(cleaned, random, **bootstrap_args)
    pairs = [float(_vector(c, "cleaned").mean() - _vector(r, "random").mean()) for c, r in zip(cleaned, random)]
    if boot["low"] > 0 and all(d > 0 for d in pairs):
        verdict = "cleaning helped"
    elif boot["high"] < 0 and all(d < 0 for d in pairs):
        verdict = "cleaning hurt"
    else:
        verdict = "no detectable difference"
    return {"verdict": verdict, "seed_pair_differences": pairs, **boot}
