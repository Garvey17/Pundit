# analyzer.py
# MatchAnalyzer provides two things:
#   1. A simple win/draw/loss percentage "fun prediction" from last 5 results.
#   2. AI-generated text (previews, summaries, trivia) via the Gemini API.

import os
from dotenv import load_dotenv
# from google import genai
from openai import OpenAI
from models import Match

load_dotenv()

class MatchAnalyzer:
    """Analyses past results and generates AI commentary via Gemini."""

    SYSTEM_PROMPT = (
        "You are a friendly, knowledgeable sports commentator writing short "
        "content for a fan companion app. You will receive a prompt asking "
        "for one of: a pre-match preview, a post-match summary, or team trivia.\n\n"
        "Rules:\n"
        "- Write in an upbeat, casual, fan-friendly tone — like a knowledgeable "
        "friend, not a formal news report.\n"
        "- Keep responses concise: 3-5 sentences for previews/summaries, or "
        "3-4 short bullet points for trivia.\n"
        "- Base your response only on the facts given in the user's prompt. "
        "Do not invent scores, player names, injuries, or events that weren't "
        "provided.\n"
        "- If the prompt doesn't include enough information to answer "
        "confidently, say so briefly instead of guessing.\n"
        "- Never state a match outcome as guaranteed or certain — frame any "
        "forward-looking comments as possibilities, not predictions.\n"
        "- Do not use markdown headers or code blocks. Plain text or simple "
        "bullet points only."
    )

    def __init__(self):
        # Create the Gemini client using the API key from the environment.
        # app.py should check that GEMINI_API_KEY is set before relying on
        # generate_ai_text(), but this class stays safe even if it's missing --
        # generate_ai_text() will just fail gracefully and return a fallback message.
        api_key =os.getenv('OPENAI_API_KEY', "")
        self.client = OpenAI(api_key=api_key)
        self.model_name = "gpt-4o-mini"

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
            # Parse the score string to find the winner
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
        Send a prompt to the Openai API and return the response text.
        Returns a friendly fallback message if the API call fails.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role":"system", "content":self.SYSTEM_PROMPT},
                    {"role":"user", "content":prompt}]
            )
            # response.text can be empty/None if the response was blocked
            return response.choices[0].message.content or "⚠️ AI returned an empty response. Try again."
        except Exception as e:
            # Catch all Gemini/network errors and return a user-friendly message
            return f"⚠️ AI generation failed: {e}\n\nTry again in a moment."