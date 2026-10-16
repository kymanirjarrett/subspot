import numpy as np
import pytest

from subspot_ml.evaluation.metrics import brier_score, log_loss


def test_uniform_forecast_log_loss_is_log3() -> None:
    probs = np.full((3, 3), 1 / 3)
    assert log_loss(probs, ["H", "D", "A"]) == pytest.approx(np.log(3))


def test_perfect_forecast_scores_zero() -> None:
    probs = np.array([[1.0, 0.0, 0.0], [0.0, 0.0, 1.0]])
    assert brier_score(probs, ["H", "A"]) == pytest.approx(0.0)
    assert log_loss(probs, ["H", "A"]) == pytest.approx(0.0, abs=1e-12)


def test_confident_wrong_forecast_is_punished() -> None:
    confident_wrong = np.array([[0.9, 0.05, 0.05]])
    hedged = np.array([[0.5, 0.25, 0.25]])
    assert log_loss(confident_wrong, ["A"]) > log_loss(hedged, ["A"])
