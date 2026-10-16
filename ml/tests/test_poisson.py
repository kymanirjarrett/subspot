import numpy as np
import pandas as pd
import pytest

from subspot_ml.models.poisson import PoissonBaseline

TRUE_ATTACK = {"a": 0.4, "b": 0.1, "c": -0.1, "d": -0.4}
TRUE_DEFENCE = {"a": 0.3, "b": 0.0, "c": 0.0, "d": -0.3}
TRUE_HOME_ADV = 0.25


@pytest.fixture(scope="module")
def synthetic_season() -> pd.DataFrame:
    """Many round-robins drawn from known ratings, so the fit can be checked against truth."""
    rng = np.random.default_rng(0)
    rows = []
    for _ in range(150):
        for home in TRUE_ATTACK:
            for away in TRUE_ATTACK:
                if home == away:
                    continue
                mu_h = np.exp(TRUE_HOME_ADV + TRUE_ATTACK[home] - TRUE_DEFENCE[away])
                mu_a = np.exp(TRUE_ATTACK[away] - TRUE_DEFENCE[home])
                rows.append((home, away, rng.poisson(mu_h), rng.poisson(mu_a)))
    return pd.DataFrame(rows, columns=["home", "away", "home_goals", "away_goals"])


def test_fit_recovers_known_ratings(synthetic_season: pd.DataFrame) -> None:
    model = PoissonBaseline().fit(synthetic_season)
    r = model.ratings
    assert r is not None
    assert r.home_advantage == pytest.approx(TRUE_HOME_ADV, abs=0.05)
    fitted = dict(zip(r.teams, r.attack, strict=True))
    for team, true_value in TRUE_ATTACK.items():
        assert fitted[team] == pytest.approx(true_value, abs=0.07)


def test_predictions_are_valid_and_ordered(synthetic_season: pd.DataFrame) -> None:
    model = PoissonBaseline().fit(synthetic_season)
    strong_home = model.predict_outcomes("a", "d")
    assert strong_home.sum() == pytest.approx(1.0)
    assert strong_home[0] > strong_home[2]  # best team at home should be favourite


def test_predict_before_fit_raises() -> None:
    with pytest.raises(RuntimeError, match="fit"):
        PoissonBaseline().predict_outcomes("a", "b")
