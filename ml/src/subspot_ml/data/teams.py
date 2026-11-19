"""Map every source's spelling of a club to one canonical team id.

football-data.co.uk, Understat and the odds feeds all spell clubs differently
("Man United", "Manchester United"). Joining sources on raw names silently
drops matches, so every name goes through ``canonical_team`` and unknown names
fail loudly instead of being guessed.
"""

from __future__ import annotations

from collections.abc import Iterable

_ALIASES: dict[str, str] = {
    "arsenal": "arsenal",
    "aston villa": "aston_villa",
    "bournemouth": "bournemouth",
    "afc bournemouth": "bournemouth",
    "brentford": "brentford",
    "brighton": "brighton",
    "brighton and hove albion": "brighton",
    "burnley": "burnley",
    "chelsea": "chelsea",
    "crystal palace": "crystal_palace",
    "everton": "everton",
    "fulham": "fulham",
    "ipswich": "ipswich",
    "ipswich town": "ipswich",
    "leeds": "leeds",
    "leeds united": "leeds",
    "leicester": "leicester",
    "leicester city": "leicester",
    "liverpool": "liverpool",
    "luton": "luton",
    "luton town": "luton",
    "man city": "man_city",
    "manchester city": "man_city",
    "man united": "man_united",
    "manchester united": "man_united",
    "newcastle": "newcastle",
    "newcastle united": "newcastle",
    "nott'm forest": "nottm_forest",
    "nottingham forest": "nottm_forest",
    "sheffield united": "sheffield_united",
    "sheffield utd": "sheffield_united",
    "southampton": "southampton",
    "sunderland": "sunderland",
    "tottenham": "tottenham",
    "tottenham hotspur": "tottenham",
    "spurs": "tottenham",
    "west ham": "west_ham",
    "west ham united": "west_ham",
    "wolves": "wolves",
    "wolverhampton wanderers": "wolves",
}


class UnknownTeamError(KeyError):
    """Raised when a source uses a team name with no entry in ``_ALIASES``."""

    def __str__(self) -> str:
        return str(self.args[0]) if self.args else ""


def _normalize(name: str) -> str:
    return " ".join(name.split()).lower()


def canonical_team(name: str) -> str:
    """Return the canonical id for ``name``, ignoring case and extra whitespace."""
    try:
        return _ALIASES[_normalize(name)]
    except KeyError:
        raise UnknownTeamError(
            f"Unknown team name {name!r}. Add it to _ALIASES in subspot_ml/data/teams.py."
        ) from None


def unmapped(names: Iterable[str]) -> set[str]:
    """Return the names that ``canonical_team`` cannot resolve."""
    return {name for name in names if _normalize(name) not in _ALIASES}
