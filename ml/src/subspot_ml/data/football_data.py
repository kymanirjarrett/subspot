"""Load Premier League results and closing odds from football-data.co.uk."""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd

from subspot_ml.data.teams import canonical_team

BASE_URL = "https://www.football-data.co.uk/mmz4281"

# Pinnacle closing odds: the sharpest public benchmark for a forecast.
_CLOSING_COLUMNS = {"PSCH": "close_home", "PSCD": "close_draw", "PSCA": "close_away"}

COLUMNS = [
    "date",
    "home",
    "away",
    "home_goals",
    "away_goals",
    "result",
    "close_home",
    "close_draw",
    "close_away",
]


def season_url(season: str) -> str:
    """URL of one Premier League season's CSV, e.g. ``season_url("2425")``."""
    if not re.fullmatch(r"\d{4}", season) or (int(season[:2]) + 1) % 100 != int(season[2:]):
        raise ValueError(f"season must look like '2425' (2024-25), got {season!r}")
    return f"{BASE_URL}/{season}/E0.csv"


def _parse_dates(raw: pd.Series) -> pd.Series:
    four_digit = pd.to_datetime(raw, format="%d/%m/%Y", errors="coerce")
    two_digit = pd.to_datetime(raw, format="%d/%m/%y", errors="coerce")
    return four_digit.fillna(two_digit)


def load_matches(path: str | Path) -> pd.DataFrame:
    """Read one season CSV into canonical columns, sorted by date.

    Unplayed fixtures are dropped and every team name is canonicalized, so an
    unknown spelling raises ``UnknownTeamError`` instead of losing the match.
    """
    raw = pd.read_csv(path, encoding="latin-1")
    played = raw.dropna(subset=["FTHG", "FTAG"]).copy()

    home_goals = played["FTHG"].astype(int)
    away_goals = played["FTAG"].astype(int)
    result = np.select([home_goals > away_goals, home_goals < away_goals], ["H", "A"], default="D")

    df = pd.DataFrame(
        {
            "date": _parse_dates(played["Date"]),
            "home": played["HomeTeam"].map(canonical_team),
            "away": played["AwayTeam"].map(canonical_team),
            "home_goals": home_goals,
            "away_goals": away_goals,
            "result": result,
        }
    )
    for source, target in _CLOSING_COLUMNS.items():
        df[target] = played[source].astype(float) if source in played else np.nan

    return df.sort_values("date", kind="stable").reset_index(drop=True)[COLUMNS]


def implied_probabilities(home: float, draw: float, away: float) -> tuple[float, float, float]:
    """Turn decimal odds into probabilities, removing the bookmaker margin."""
    inverse = np.array([1 / home, 1 / draw, 1 / away])
    probs = inverse / inverse.sum()
    return float(probs[0]), float(probs[1]), float(probs[2])
