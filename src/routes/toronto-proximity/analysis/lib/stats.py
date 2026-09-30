"""
Population-weighted summary statistics used throughout the analysis
"""
import numpy as np


def weighted_mean(values, weights):
    return float(np.average(values, weights=weights))


def weighted_percentile(values, weights, q):
    """Population-weighted percentile (q in 0-100)."""
    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)
    order = np.argsort(values)
    v, w = values[order], weights[order]
    cum = np.cumsum(w) / w.sum()
    return float(np.interp(q / 100, cum, v))


def weighted_share(values, weights, lo, hi):
    """Population share (%) of hexes with lo <= value < hi."""
    values = np.asarray(values, dtype=float)
    weights = np.asarray(weights, dtype=float)
    mask = (values >= lo) & (values < hi)
    return float(weights[mask].sum() / weights.sum() * 100)
