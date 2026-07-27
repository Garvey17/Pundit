# api_client.py
# Wraps all calls to TheSportsDB free API (v1).
# Each method handles its own errors and returns None / [] on failure
# so the UI layer never has to deal with raw exceptions.

import requests
from models import Team, Match

# Base URL for TheSportsDB free tier (no API key required for v1)
BASE_URL = "https://www.thesportsdb.com/api/v1/json/3"


class SportsAPIClient:
    """Handles fetching team info, upcoming fixtures, and past results."""

    def search_team(self, name: str) -> Team | None:
        """
        Search for a team by name and return a Team object, or None if not found.
        Uses the /searchteams.php endpoint.
        """
        try:
            url = f"{BASE_URL}/searchteams.php"
            response = requests.get(url, params={"t": name}, timeout=10)
            response.raise_for_status()
            data = response.json()

            # API returns {"teams": null} when nothing is found
            teams = data.get("teams")
            if not teams:
                return None

            t = teams[0]  # Use the first result
            return Team(
                name=t.get("strTeam", "Unknown"),
                team_id=t.get("idTeam", ""),
                league=t.get("strLeague", "Unknown League"),
                badge_url=t.get("strTeamBadge", ""),
            )

        except (requests.RequestException, ValueError, KeyError):
            # Covers timeouts, connection errors, and malformed JSON
            return None

    def get_upcoming_fixtures(self, team_id: str) -> list[Match]:
        """
        Fetch the next 5 scheduled matches for a team.
        Returns an empty list if none are found or the request fails.
        Uses the /eventsnext.php endpoint.
        """
        try:
            url = f"{BASE_URL}/eventsnext.php"
            response = requests.get(url, params={"id": team_id}, timeout=10)
            response.raise_for_status()
            data = response.json()

            events = data.get("events")
            if not events:
                return []

            matches = []
            for e in events:
                match = Match(
                    home_team=e.get("strHomeTeam", "?"),
                    away_team=e.get("strAwayTeam", "?"),
                    date=e.get("dateEvent", "Unknown date"),
                    score=None,  # Upcoming — no score yet
                    competition=e.get("strLeague", "Unknown"),
                )
                matches.append(match)
            return matches

        except (requests.RequestException, ValueError, KeyError):
            return []

    def get_past_results(self, team_id: str) -> list[Match]:
        """
        Fetch the last 5 completed matches for a team.
        Returns an empty list if none are found or the request fails.
        Uses the /eventslast.php endpoint.
        """
        try:
            url = f"{BASE_URL}/eventslast.php"
            response = requests.get(url, params={"id": team_id}, timeout=10)
            response.raise_for_status()
            data = response.json()

            results = data.get("results")
            if not results:
                return []

            matches = []
            for e in results:
                # Build score string from home/away goals if available
                home_goals = e.get("intHomeScore")
                away_goals = e.get("intAwayScore")
                if home_goals is not None and away_goals is not None:
                    score = f"{home_goals}-{away_goals}"
                else:
                    score = None

                match = Match(
                    home_team=e.get("strHomeTeam", "?"),
                    away_team=e.get("strAwayTeam", "?"),
                    date=e.get("dateEvent", "Unknown date"),
                    score=score,
                    competition=e.get("strLeague", "Unknown"),
                )
                matches.append(match)
            return matches

        except (requests.RequestException, ValueError, KeyError):
            return []
