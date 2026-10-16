from pathlib import Path

import pytest

from subspot_ml.data.football_data import implied_probabilities, load_matches, season_url
from subspot_ml.data.teams import UnknownTeamError


def test_load_matches_canonicalizes_and_drops_unplayed(sample_csv: Path) -> None:
    df = load_matches(sample_csv)
    assert len(df) == 7  # the unplayed Liverpool v Arsenal row is dropped
    assert df.loc[0, "home"] == "man_united"
    assert list(df["result"][:2]) == ["H", "A"]
    assert df["date"].is_monotonic_increasing


def test_closing_odds_are_kept(sample_csv: Path) -> None:
    df = load_matches(sample_csv)
    assert df.loc[0, ["close_home", "close_draw", "close_away"]].tolist() == [1.62, 4.10, 5.40]


def test_unknown_team_in_source_raises(tmp_path: Path) -> None:
    path = tmp_path / "bad.csv"
    path.write_text("Date,HomeTeam,AwayTeam,FTHG,FTAG\n16/08/2024,Arsenal,Atletico,1,0\n")
    with pytest.raises(UnknownTeamError, match="Atletico"):
        load_matches(path)


def test_implied_probabilities_remove_margin() -> None:
    probs = implied_probabilities(1.62, 4.10, 5.40)
    assert sum(probs) == pytest.approx(1.0)
    assert probs[0] > probs[1] > 0


def test_season_url() -> None:
    assert season_url("2425").endswith("/mmz4281/2425/E0.csv")
    with pytest.raises(ValueError):
        season_url("2024-25")
