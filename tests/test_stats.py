"""stats.py against scipy and statsmodels, and against values pinned from them (16 Nov 2026,
scipy 1.18.1, statsmodels 0.15.0) so plain CI checks the same numbers without those libraries."""
import math

import numpy as np
import pytest

from finqa_lora import stats

# (k, n, low, high) from statsmodels proportion_confint(k, n, method="wilson")
WILSON = [
    (0, 50, 0.0, 0.07134759913335874),
    (50, 50, 0.9286524008666412, 1.0),
    (1, 50, 0.003539259271646236, 0.10495443589637815),
    (29, 883, 0.022963019127505195, 0.046769240461406895),
    (224, 883, 0.22609048950489818, 0.28340470191471),
    (631, 1147, 0.521220989618862, 0.578705893548733),
]
# (right in a only, right in b only, p) from statsmodels mcnemar(exact=True); scipy binomtest agrees
MCNEMAR = [(0, 0, 1.0), (1, 0, 1.0), (5, 5, 1.0), (10, 3, 0.09228515625),
           (48, 30, 0.053544392168502264), (130, 100, 0.05561357778139238), (3, 17, 0.0025768280029296875)]


def pair(a_only, b_only, both=7, neither=4):
    a = [1] * a_only + [0] * b_only + [1] * both + [0] * neither
    b = [0] * a_only + [1] * b_only + [1] * both + [0] * neither
    return a, b


@pytest.mark.parametrize("k, n, low, high", WILSON)
def test_wilson_matches_pinned_statsmodels(k, n, low, high):
    assert stats.wilson(k, n) == pytest.approx((low, high), abs=1e-12)


@pytest.mark.parametrize("a_only, b_only, p", MCNEMAR)
def test_mcnemar_matches_pinned_statsmodels(a_only, b_only, p):
    r = stats.mcnemar_exact(*pair(a_only, b_only))
    assert (r["a_only"], r["b_only"], r["discordant"]) == (a_only, b_only, a_only + b_only)
    assert r["p"] == pytest.approx(p, abs=1e-15)


def test_mcnemar_is_symmetric_and_ignores_concordant_items():
    a, b = pair(48, 30, both=500, neither=300)
    assert stats.mcnemar_exact(a, b)["p"] == stats.mcnemar_exact(b, a)["p"] == pytest.approx(0.053544392168502264)


def test_live_cross_check_with_scipy_and_statsmodels():
    proportion = pytest.importorskip("statsmodels.stats.proportion")
    tables = pytest.importorskip("statsmodels.stats.contingency_tables")
    scipy_stats = pytest.importorskip("scipy.stats")
    for k in range(0, 1148, 37):
        assert stats.wilson(k, 1147) == pytest.approx(proportion.proportion_confint(k, 1147, method="wilson"),
                                                       abs=1e-12)
    for a_only in range(0, 60, 7):
        for b_only in range(0, 60, 11):
            p = stats.mcnemar_exact(*pair(a_only, b_only))["p"]
            assert p == pytest.approx(tables.mcnemar([[0, a_only], [b_only, 0]], exact=True).pvalue, abs=1e-12)
            if a_only + b_only:
                assert p == pytest.approx(scipy_stats.binomtest(a_only, a_only + b_only).pvalue, abs=1e-12)


@pytest.mark.parametrize("bad", [[0, 1, 2], [[0, 1]], [0.5, 1]])
def test_vectors_must_be_per_item_zero_one(bad):
    with pytest.raises(ValueError):
        stats.mcnemar_exact(bad, bad)


def test_vectors_must_cover_the_same_items():
    with pytest.raises(ValueError):
        stats.mcnemar_exact([1, 0], [1, 0, 1])


def runs(rng, n, accuracies):
    return [(rng.random(n) < acc).astype(int) for acc in accuracies]


def test_bootstrap_difference_and_interval():
    rng = np.random.default_rng(0)
    c, r = runs(rng, 1147, [0.60, 0.61, 0.59]), runs(rng, 1147, [0.55, 0.56, 0.54])
    out = stats.paired_bootstrap(c, r)
    per_item = np.mean(c, axis=0) - np.mean(r, axis=0)
    assert out["difference"] == pytest.approx(per_item.mean(), abs=1e-15)
    assert out["low"] < out["difference"] < out["high"]
    # Percentile interval is close to mean +- 1.96 standard errors for a mean of 1,147 items.
    se = per_item.std(ddof=1) / math.sqrt(per_item.size)
    assert out["low"] == pytest.approx(out["difference"] - stats.Z95 * se, abs=0.003)
    assert out["high"] == pytest.approx(out["difference"] + stats.Z95 * se, abs=0.003)
    assert stats.paired_bootstrap(c, r) == out              # fixed seed: same interval every time


def test_bootstrap_agrees_with_scipy():
    scipy_stats = pytest.importorskip("scipy.stats")
    rng = np.random.default_rng(1)
    c, r = runs(rng, 883, [0.5, 0.52]), runs(rng, 883, [0.48, 0.47])
    out = stats.paired_bootstrap(c, r)
    per_item = np.mean(c, axis=0) - np.mean(r, axis=0)
    ref = scipy_stats.bootstrap((per_item,), np.mean, n_resamples=10_000, method="percentile",
                                random_state=np.random.default_rng(2)).confidence_interval
    assert (out["low"], out["high"]) == pytest.approx((ref.low, ref.high), abs=0.003)


def test_winner_helped_needs_interval_and_every_seed_pair():
    rng = np.random.default_rng(3)
    base = runs(rng, 1147, [0.55, 0.55, 0.55])
    better = [np.where(rng.random(1147) < 0.12, 1, b) for b in base]      # about +5 points per seed
    assert stats.winner(better, base)["verdict"] == "cleaning helped"
    assert stats.winner(base, better)["verdict"] == "cleaning hurt"


def test_winner_mixed_seed_pairs_is_no_difference_even_with_a_clear_interval():
    # Two seed pairs strongly favour cleaning; one pair favours random by 1 item.
    shared = np.zeros(1147, dtype=int)
    c = [shared.copy() for _ in range(3)]
    r = [shared.copy() for _ in range(3)]
    c[0][:150] = 1
    c[1][:150] = 1
    r[2][:1] = 1
    out = stats.winner(c, r)
    assert out["low"] > 0
    assert [d > 0 for d in out["seed_pair_differences"]] == [True, True, False]
    assert out["verdict"] == "no detectable difference"


def test_winner_interval_crossing_zero_is_no_difference():
    rng = np.random.default_rng(4)
    same = runs(rng, 1147, [0.55, 0.55, 0.55]), runs(rng, 1147, [0.55, 0.55, 0.55])
    out = stats.winner(*same)
    assert out["low"] < 0 < out["high"] and out["verdict"] == "no detectable difference"


def test_winner_needs_one_random_partner_per_seed():
    with pytest.raises(ValueError):
        stats.winner([[1, 0]] * 3, [[1, 0]] * 2)
