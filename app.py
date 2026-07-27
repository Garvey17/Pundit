# app.py
# Main entry point — run with: streamlit run app.py
# Single-page Streamlit app with tabs for fixtures, results, AI content, and trivia.

import os
import streamlit as st

from api_client import SportsAPIClient
from analyzer import MatchAnalyzer
from storage import load_data, save_data
from utils import clean_team_name

# ── Page config (must be the very first Streamlit call) ──────────────────────
st.set_page_config(
    page_title="Sports Match Analyzer",
    page_icon="⚽",
    layout="wide",
)

# ── Custom CSS for a cleaner look ─────────────────────────────────────────────
st.markdown(
    """
    <style>
        .team-badge { border-radius: 8px; }
        .section-header { font-size: 1.1rem; font-weight: 600; margin-bottom: 0.25rem; }
        .match-card {
            background: #1e1e2e;
            border-radius: 10px;
            padding: 12px 16px;
            margin-bottom: 8px;
            border-left: 4px solid #7c6af7;
        }
        .prediction-box {
            background: #0f3460;
            border-radius: 10px;
            padding: 14px 18px;
            border-left: 4px solid #e94560;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Shared objects (created once per session via session state) ───────────────
if "api" not in st.session_state:
    st.session_state.api = SportsAPIClient()
if "analyzer" not in st.session_state:
    st.session_state.analyzer = MatchAnalyzer()

api: SportsAPIClient = st.session_state.api
analyzer: MatchAnalyzer = st.session_state.analyzer

# ── Sidebar: Favourites ───────────────────────────────────────────────────────
st.sidebar.title("⭐ My Favourites")
data = load_data()
favourites: list = data.get("favourites", [])

if favourites:
    for fav in favourites:
        # Clicking a favourite loads it into the search box via session state
        if st.sidebar.button(fav, key=f"fav_{fav}"):
            st.session_state["search_query"] = fav
else:
    st.sidebar.info("No favourites yet. Search for a team and bookmark it!")

st.sidebar.markdown("---")
st.sidebar.markdown(
    "🔑 **API Keys needed**\n\n"
    "Set `GEMINI_API_KEY` as an environment variable before running."
)

# ── Main header ───────────────────────────────────────────────────────────────
st.title("⚽ Sports Match Analyzer & Fan Companion")
st.markdown("Search for any football team to see fixtures, results, and AI-generated content.")

# ── Search bar ────────────────────────────────────────────────────────────────
# Pre-fill the search box if a favourite was clicked in the sidebar
default_query = st.session_state.get("search_query", "")
team_query = st.text_input(
    "🔍 Search for a team",
    value=default_query,
    placeholder="e.g. Arsenal, Barcelona, Liverpool…",
    key="team_search_input",
)

search_clicked = st.button("Search", type="primary")

# ── Team search and display ───────────────────────────────────────────────────
if search_clicked and team_query.strip():
    # Clean and standardize the input before sending to the API
    clean_name = clean_team_name(team_query)
    st.session_state["search_query"] = clean_name  # Keep for re-renders

    with st.spinner(f"Looking up **{clean_name}**…"):
        team = api.search_team(clean_name)

    if team is None:
        st.error(
            f"❌ No team found for **'{clean_name}'**. "
            "Check the spelling or try a different name."
        )
    else:
        # Store found team in session state so tabs can use it
        st.session_state["team"] = team

# Only render the rest if we have a team loaded
if "team" in st.session_state:
    team = st.session_state["team"]
    data = load_data()  # Reload in case sidebar added/removed favourites

    # ── Team header ──────────────────────────────────────────────────────────
    col_badge, col_info = st.columns([1, 4])
    with col_badge:
        if team.badge_url:
            st.image(team.badge_url, width=100, caption=team.name)
        else:
            st.markdown("🏆")  # Fallback icon if no badge available

    with col_info:
        st.subheader(team.name)
        st.markdown(f"**League:** {team.league}")
        st.markdown(f"**Team ID:** `{team.team_id}`")

        # Bookmark button
        is_bookmarked = team.name in data.get("favourites", [])
        btn_label = "✅ Bookmarked!" if is_bookmarked else "⭐ Bookmark this team"
        if st.button(btn_label, key="bookmark_btn"):
            if not is_bookmarked:
                data["favourites"].append(team.name)
                save_data(data)
                st.success(f"**{team.name}** added to favourites!")
                st.rerun()
            else:
                data["favourites"].remove(team.name)
                save_data(data)
                st.info(f"**{team.name}** removed from favourites.")
                st.rerun()

    st.markdown("---")

    # ── Tabs ─────────────────────────────────────────────────────────────────
    tab_fix, tab_res, tab_ai, tab_trivia = st.tabs(
        ["📅 Upcoming Fixtures", "📋 Past Results", "🤖 AI Preview / Summary", "🧠 Trivia"]
    )

    # ── Tab 1: Upcoming Fixtures ──────────────────────────────────────────────
    with tab_fix:
        st.markdown("### Next Fixtures")
        with st.spinner("Fetching upcoming fixtures…"):
            fixtures = api.get_upcoming_fixtures(team.team_id)

        if not fixtures:
            st.warning("⚠️ No upcoming fixtures found for this team.")
        else:
            for m in fixtures:
                st.markdown(
                    f"""<div class="match-card">
                        <b>{m.home_team}</b> vs <b>{m.away_team}</b><br/>
                        📅 {m.date} &nbsp;|&nbsp; 🏆 {m.competition} &nbsp;|&nbsp; Score: {m.get_score_string()}
                    </div>""",
                    unsafe_allow_html=True,
                )

    # ── Tab 2: Past Results ───────────────────────────────────────────────────
    with tab_res:
        st.markdown("### Recent Results")
        with st.spinner("Fetching past results…"):
            past = api.get_past_results(team.team_id)

        if not past:
            st.warning("⚠️ No past results found for this team.")
        else:
            for m in past:
                score_display = m.get_score_string()
                st.markdown(
                    f"""<div class="match-card">
                        <b>{m.home_team}</b> {score_display} <b>{m.away_team}</b><br/>
                        📅 {m.date} &nbsp;|&nbsp; 🏆 {m.competition}
                    </div>""",
                    unsafe_allow_html=True,
                )

        # ── 🎲 Fun Match Prediction (lives inside Past Results tab) ───────────
        st.markdown("---")
        st.markdown("### 🎲 Fun Match Prediction")
        st.markdown(
            "_Based on recent form — this is a fun estimate, **not** a guaranteed prediction!_"
        )
        if past:
            prediction_text = analyzer.predict_outcome(past, team.name)
            st.markdown(
                f'<div class="prediction-box">{prediction_text}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.info("No past results available to generate a prediction.")

    # ── Tab 3: AI Preview / Summary ───────────────────────────────────────────
    with tab_ai:
        st.markdown("### 🤖 AI-Generated Content")
        st.markdown(
            "Click a button to generate content via Gemini. "
            "Results are saved locally so you don't have to regenerate every visit."
        )

        # Check for a cached summary for this team
        cached = data.get("cached_summaries", {}).get(team.name, "")
        if cached:
            st.info("📝 Showing cached AI summary (click **Regenerate** to refresh).")
            st.markdown(cached)

        col_pre, col_sum, col_regen = st.columns(3)

        with col_pre:
            if st.button("⚡ Pre-match Preview", key="btn_preview"):
                prompt = (
                    f"Write an exciting 150-word pre-match preview for {team.name}'s "
                    f"next match in the {team.league}. Include team strengths and what fans "
                    f"should watch out for. Keep it energetic and fan-friendly."
                )
                with st.spinner("Generating preview…"):
                    text = analyzer.generate_ai_text(prompt)
                data["cached_summaries"][team.name] = text
                save_data(data)
                st.markdown(text)

        with col_sum:
            if st.button("📊 Post-match Summary", key="btn_summary"):
                prompt = (
                    f"Write a 150-word post-match summary for {team.name}'s most recent "
                    f"match in the {team.league}. Discuss key moments, player performances, "
                    f"and what it means for the rest of the season."
                )
                with st.spinner("Generating summary…"):
                    text = analyzer.generate_ai_text(prompt)
                data["cached_summaries"][team.name] = text
                save_data(data)
                st.markdown(text)

        with col_regen:
            if cached and st.button("🔄 Regenerate", key="btn_regen"):
                # Clear the cache so the next button press fetches fresh content
                data["cached_summaries"].pop(team.name, None)
                save_data(data)
                st.rerun()

    # ── Tab 4: Trivia ─────────────────────────────────────────────────────────
    with tab_trivia:
        st.markdown("### 🧠 Team Trivia")
        st.markdown(
            "Let Gemini generate some fun facts about your team."
        )

        if st.button("✨ Generate Trivia", key="btn_trivia"):
            prompt = (
                f"Give me 5 interesting and surprising facts about {team.name} football club. "
                f"Format them as a numbered list. Keep each fact to 1-2 sentences."
            )
            with st.spinner("Generating trivia…"):
                trivia_text = analyzer.generate_ai_text(prompt)
            st.markdown(trivia_text)

    # ── Personal Notes ────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📝 My Notes")
    st.markdown(f"_Save a personal note about **{team.name}**_")

    existing_note = data.get("notes", {}).get(team.name, "")
    note_text = st.text_area(
        "Your note",
        value=existing_note,
        placeholder="Add thoughts, predictions, or reminders here…",
        height=120,
        key="note_area",
    )

    if st.button("💾 Save Note", key="save_note_btn"):
        data["notes"][team.name] = note_text
        save_data(data)
        st.success("Note saved!")

elif not search_clicked:
    # Landing state — no search attempted yet
    st.markdown(
        """
        <div style="text-align:center; padding: 60px 0; color: #aaa;">
            <h2>👋 Welcome!</h2>
            <p>Type a team name above and hit <strong>Search</strong> to get started.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
