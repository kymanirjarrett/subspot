import pytest

from subspot_ml.data.teams import UnknownTeamError, canonical_team, unmapped


@pytest.mark.parametrize(
    ("source_name", "expected"),
    [
        ("Man United", "man_united"),  # football-data.co.uk
        ("Manchester United", "man_united"),  # Understat
        ("Nott'm Forest", "nottm_forest"),
        ("Wolverhampton Wanderers", "wolves"),
        ("  tottenham ", "tottenham"),  # whitespace and case are normalized
    ],
)
def test_aliases_resolve_to_one_id(source_name: str, expected: str) -> None:
    assert canonical_team(source_name) == expected


def test_unknown_team_fails_loudly() -> None:
    with pytest.raises(UnknownTeamError, match="Add it to _ALIASES"):
        canonical_team("Manchester Utd FC")


def test_unmapped_reports_only_unknown_names() -> None:
    assert unmapped(["Arsenal", "Real Madrid", "Spurs"]) == {"Real Madrid"}
