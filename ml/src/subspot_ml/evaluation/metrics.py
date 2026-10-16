"""Scoring rules for 3-way (home/draw/away) forecasts. Lower is better for both."""

from __future__ import annotations

import numpy as np

OUTCOMES = ("H", "D", "A")


def _one_hot(results: list[str] | np.ndarray) -> np.ndarray:
    index = {o: i for i, o in enumerate(OUTCOMES)}
    results = np.asarray(results)
    encoded = np.zeros((len(results), 3))
    encoded[np.arange(len(results)), [index[r] for r in results]] = 1.0
    return encoded


def log_loss(probs: np.ndarray, results: list[str] | np.ndarray, eps: float = 1e-15) -> float:
    """Mean negative log probability assigned to what actually happened."""
    probs = np.clip(np.asarray(probs, dtype=float), eps, 1.0)
    return float(-(np.log(probs) * _one_hot(results)).sum(axis=1).mean())


def brier_score(probs: np.ndarray, results: list[str] | np.ndarray) -> float:
    """Mean squared error between the probability vector and the one-hot outcome."""
    probs = np.asarray(probs, dtype=float)
    return float(((probs - _one_hot(results)) ** 2).sum(axis=1).mean())
