# models.py
# Simple data classes representing a Team and a Match.
# No complex logic here — just store data and provide a helper method.


class Team:
    """Holds basic information about a football/sports team."""

    def __init__(self, name: str, team_id: str, league: str, badge_url: str):
        self.name = name          # Team display name, e.g. "Arsenal"
        self.team_id = team_id    # TheSportsDB internal ID
        self.league = league      # League/competition name
        self.badge_url = badge_url  # URL to the team's badge/crest image


class Match:
    """Represents a single match — either upcoming or already played."""

    def __init__(
        self,
        home_team: str,
        away_team: str,
        date: str,
        score: str | None,
        competition: str,
    ):
        self.home_team = home_team    # Name of the home side
        self.away_team = away_team    # Name of the away side
        self.date = date              # Match date string (YYYY-MM-DD or similar)
        self.score = score            # e.g. "2-1", or None if not played yet
        self.competition = competition  # League/cup name

    def get_score_string(self) -> str:
        """Return a display-ready score or 'TBD' for unplayed matches."""
        if self.score:
            return self.score
        return "TBD"
