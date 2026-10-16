"""Phase 1 baseline: independent Poisson goals with attack/defence ratings (Maher, 1982).

log(home_rate) = home_adv + attack[home] - defence[away]
log(away_rate) =            attack[away] - defence[home]

Fitted by maximum likelihood. This is the number the PyTorch model has to beat on log loss.
Dixon-Coles (low-score correction + time decay) is the next step on the roadmap.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import gammaln
from scipy.stats import poisson


@dataclass(frozen=True)
class FittedRatings:
    teams: tuple[str, ...]
    attack: np.ndarray
    defence: np.ndarray
    home_advantage: float


class PoissonBaseline:
    def __init__(self, l2: float = 1e-3) -> None:
        # Small ridge penalty keeps ratings finite for teams with very few matches.
        self.l2 = l2
        self.ratings: FittedRatings | None = None

    def fit(self, matches: pd.DataFrame) -> PoissonBaseline:
        teams = tuple(sorted(set(matches["home"]) | set(matches["away"])))
        index = {t: i for i, t in enumerate(teams)}
        h = matches["home"].map(index).to_numpy()
        a = matches["away"].map(index).to_numpy()
        hg = matches["home_goals"].to_numpy(dtype=float)
        ag = matches["away_goals"].to_numpy(dtype=float)
        n = len(teams)
        const = gammaln(hg + 1).sum() + gammaln(ag + 1).sum()

        def unpack(theta: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
            attack = theta[:n] - theta[:n].mean()  # identifiability: ratings centred on 0
            defence = theta[n : 2 * n] - theta[n : 2 * n].mean()
            return attack, defence, theta[-1]

        def neg_log_likelihood(theta: np.ndarray) -> float:
            attack, defence, home_adv = unpack(theta)
            log_mu_h = home_adv + attack[h] - defence[a]
            log_mu_a = attack[a] - defence[h]
            ll = (hg * log_mu_h - np.exp(log_mu_h)).sum() + (ag * log_mu_a - np.exp(log_mu_a)).sum()
            return -(ll - const) + self.l2 * float(theta[:-1] @ theta[:-1])

        theta0 = np.zeros(2 * n + 1)
        theta0[-1] = 0.25
        result = minimize(neg_log_likelihood, theta0, method="L-BFGS-B")
        if not result.success:
            raise RuntimeError(f"Poisson fit did not converge: {result.message}")

        attack, defence, home_adv = unpack(result.x)
        self.ratings = FittedRatings(teams, attack, defence, float(home_adv))
        return self

    def expected_goals(self, home: str, away: str) -> tuple[float, float]:
        r = self._require_fit()
        i, j = r.teams.index(home), r.teams.index(away)
        mu_h = np.exp(r.home_advantage + r.attack[i] - r.defence[j])
        mu_a = np.exp(r.attack[j] - r.defence[i])
        return float(mu_h), float(mu_a)

    def predict_outcomes(self, home: str, away: str, max_goals: int = 10) -> np.ndarray:
        """[P(home win), P(draw), P(away win)] in closed form."""
        mu_h, mu_a = self.expected_goals(home, away)
        goals = np.arange(max_goals + 1)
        grid = np.outer(poisson.pmf(goals, mu_h), poisson.pmf(goals, mu_a))
        probs = np.array([np.tril(grid, -1).sum(), np.trace(grid), np.triu(grid, 1).sum()])
        return probs / probs.sum()

    def _require_fit(self) -> FittedRatings:
        if self.ratings is None:
            raise RuntimeError("Call fit() before predicting.")
        return self.ratings
