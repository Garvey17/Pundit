# analyzer.py
# MatchAnalyzer provides two things:
#   1. A simple win/draw/loss percentage "fun prediction" from last 5 results.
#   2. AI-generated text (previews, summaries, trivia) via the Gemini API.

import os
import google.generativeai as genai
from models import Match


class MatchAnalyzer:
    """Analyses past results and generates AI commentary via Gemini."""

    def __init__(self):
        # Configure the Gemini client using the API key from the environment.
        # The app.py checks for this key before calling any method here.
        api_key = os.getenv("GEMINI_API_KEY", "")
        if api_key:
            genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")

    def predict_outcome(self, last_5_results: list[Match], team_name: str) -> str:
        """
        Count wins/draws/losses for the given team from its last 5 matches and
        return a fun percentage-based estimate string.
        Clearly labelled as a non-guaranteed estimate.
        """
        if not last_5_results:
            return "Not enough data to make a prediction."

        wins = draws = losses = 0

        for match in last_5_results:
            # Parse the score string to find winner
            score = match.get_score_string()
            if score == "TBD" or "-" not in score:
                continue
            try:
                home_goals, away_goals = map(int, score.split("-"))
            except ValueError:
                continue

            # Determine if the team was home or away, then check outcome
            if match.home_team.lower() == team_name.lower():
                if home_goals > away_goals:
                    wins += 1
                elif home_goals == away_goals:
                    draws += 1
                else:
                    losses += 1
            else:
                if away_goals > home_goals:
                    wins += 1
                elif away_goals == home_goals:
                    draws += 1
                else:
                    losses += 1

        total = wins + draws + losses
        if total == 0:
            return "Not enough scored matches to estimate."

        # Convert to percentages out of the matches that had scores
        win_pct = round((wins / total) * 100)
        draw_pct = round((draws / total) * 100)
        loss_pct = round((losses / total) * 100)

        return (
            f"📊 Based on last {total} results — "
            f"**Win**: {win_pct}% | **Draw**: {draw_pct}% | **Loss**: {loss_pct}%\n\n"
            f"🎲 *Fun estimate only — not a guaranteed prediction!*"
        )

    def generate_ai_text(self, prompt: str) -> str:
        """
        Send a prompt to the Gemini API and return the response text.
        Returns a friendly fallback message if the API call fails.
        """
        try:
            response = self.model.generate_content(prompt)
            # response.text raises if the response is blocked or empty
            return response.text
        except Exception as e:
            # Catch all Gemini/network errors and return a user-friendly message
            return f"⚠️ AI generation failed: {e}\n\nTry again in a moment."
