# app.py
# Main entry point — run with: streamlit run app.py
# Single-page Streamlit app with tabs for fixtures, results, AI content, and trivia.

import streamlit as st

from api_client import SportsAPIClient
from analyzer import MatchAnalyzer
from storage import load_data, save_data
from utils import clean_team_name

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sports Match Analyzer",
    page_icon="⚽",
    layout="wide",
)

# ── Shared instances (cached per session) ──────────────────────────────────────
if "api" not in st.session_state:
    st.session_state.api = SportsAPIClient()
if "analyzer" not in st.session_state:
    st.session_state.analyzer = MatchAnalyzer()

api: SportsAPIClient = st.session_state.api
analyzer: MatchAnalyzer = st.session_state.analyzer

# ── Sidebar: My Favourites ───────────────────────────────────────────────────
st.sidebar.title("⭐ My Favourites")
data = load_data()
favourites = data.get("favourites", [])

if favourites:
    for fav in favourites:
        if st.sidebar.button(fav, key=f"fav_{fav}"):
            st.session_state["search_query"] = fav
            st.session_state["do_search"] = True
else:
    st.sidebar.info("No favourites bookmarked yet.")

# ── Header & Search ───────────────────────────────────────────────────────────
st.title("⚽ Sports Match Analyzer & Fan Companion")

default_query = st.session_state.get("search_query", "")
team_query = st.text_input("🔍 Search Team Name", value=default_query, placeholder="e.g. Arsenal, Barcelona…")
search_clicked = st.button("Search", type="primary")

# Execute search if button clicked or favourite chosen
if search_clicked or st.session_state.pop("do_search", False):
    if team_query.strip():
        clean_name = clean_team_name(team_query)
        st.session_state["search_query"] = clean_name
        with st.spinner(f"Searching for {clean_name}…"):
            team = api.search_team(clean_name)
            if team:
                st.session_state["team"] = team
                # Fetch fixtures and past results once and store in session state
                st.session_state["fixtures"] = api.get_upcoming_fixtures(team.team_id)
                st.session_state["past"] = api.get_past_results(team.team_id)
            else:
                st.session_state.pop("team", None)
                st.error(f"❌ Team '{clean_name}' not found. Please check spelling.")

# ── Team View ─────────────────────────────────────────────────────────────────
if "team" in st.session_state:
    team = st.session_state["team"]
    fixtures = st.session_state.get("fixtures", [])
    past = st.session_state.get("past", [])
    data = load_data()

    # Team Info Header
    col_badge, col_info = st.columns([1, 4])
    with col_badge:
        if team.badge_url:
            st.image(team.badge_url, width=100)
        else:
            st.markdown("🏆")

    with col_info:
        st.subheader(team.name)
        st.write(f"**League:** {team.league} | **Team ID:** {team.team_id}")

        # Bookmark toggle button
        is_bookmarked = team.name in data.get("favourites", [])
        if st.button("✅ Bookmarked" if is_bookmarked else "⭐ Bookmark this team"):
            if is_bookmarked:
                data["favourites"].remove(team.name)
            else:
                data["favourites"].append(team.name)
            save_data(data)
            st.rerun()

    st.markdown("---")

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab_fix, tab_res, tab_ai, tab_trivia = st.tabs(
        ["📅 Upcoming Fixtures", "📋 Past Results", "🤖 AI Preview / Summary", "🧠 Trivia"]
    )

    # 1. Upcoming Fixtures Tab
    with tab_fix:
        st.subheader("Upcoming Fixtures")
        if fixtures:
            for m in fixtures:
                st.info(f"**{m.home_team}** vs **{m.away_team}** | 📅 {m.date} | 🏆 {m.competition}")
        else:
            st.warning("No upcoming fixtures found.")

    # 2. Past Results Tab & Fun Prediction
    with tab_res:
        st.subheader("Past Results")
        if past:
            for m in past:
                st.success(f"**{m.home_team}** {m.get_score_string()} **{m.away_team}** | 📅 {m.date} | 🏆 {m.competition}")
        else:
            st.warning("No past results found.")

        st.markdown("---")
        st.subheader("🎲 Fun Match Prediction")
        st.caption("Based on recent form — this is a fun estimate, NOT a guaranteed prediction!")
        if past:
            st.markdown(analyzer.predict_outcome(past, team.name))
        else:
            st.write("Not enough past match data available to compute prediction.")

    # 3. AI Preview / Summary Tab (Includes Rich Match Context in Prompt)
    with tab_ai:
        st.subheader("AI Match Commentary")

        cached = data.get("cached_summaries", {}).get(team.name, "")
        if cached:
            st.info("📝 Cached AI Commentary:")
            st.markdown(cached)

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("⚡ Pre-match Preview"):
                # Build context-rich prompt using actual upcoming fixture data
                if fixtures:
                    next_m = fixtures[0]
                    prompt = (
                        f"Write an exciting 150-word pre-match preview for {team.name}.\n"
                        f"Match Details: {next_m.home_team} vs {next_m.away_team} scheduled for {next_m.date} in {next_m.competition}.\n"
                        f"Discuss team strengths, key matchups, and expectations for this game."
                    )
                else:
                    prompt = f"Write an exciting 150-word pre-match preview for {team.name}'s upcoming games in {team.league}."

                with st.spinner("Generating pre-match preview…"):
                    ai_text = analyzer.generate_ai_text(prompt)
                data["cached_summaries"][team.name] = ai_text
                save_data(data)
                st.rerun()

        with col2:
            if st.button("📊 Post-match Summary"):
                # Build context-rich prompt using actual past match score and opponents
                if past:
                    last_m = past[0]
                    score_str = last_m.get_score_string()
                    prompt = (
                        f"Write a 150-word post-match summary for {team.name}.\n"
                        f"Match Details: {last_m.home_team} vs {last_m.away_team}, Final Score: {score_str}, Date: {last_m.date}, League: {last_m.competition}.\n"
                        f"Analyze the result, key tactical takeaways, and player performances."
                    )
                else:
                    prompt = f"Write a 150-word post-match summary for {team.name}'s recent performances in {team.league}."

                with st.spinner("Generating post-match summary…"):
                    ai_text = analyzer.generate_ai_text(prompt)
                data["cached_summaries"][team.name] = ai_text
                save_data(data)
                st.rerun()

        with col3:
            if cached and st.button("🔄 Clear Cache"):
                data["cached_summaries"].pop(team.name, None)
                save_data(data)
                st.rerun()

    # 4. Trivia Tab
    with tab_trivia:
        st.subheader("Team Trivia")
        if st.button("✨ Generate Trivia"):
            prompt = f"Provide 5 interesting and fun trivia facts about {team.name} football club as a numbered list."
            with st.spinner("Generating trivia…"):
                trivia = analyzer.generate_ai_text(prompt)
            st.markdown(trivia)

    # Personal Notes Section
    st.markdown("---")
    st.subheader("📝 Personal Team Notes")
    note_key = f"note_{team.name}"
    current_note = data.get("notes", {}).get(team.name, "")
    user_note = st.text_area("Your Notes", value=current_note, height=100, key=note_key)

    if st.button("💾 Save Note"):
        data["notes"][team.name] = user_note
        save_data(data)
        st.success("Note saved successfully!")
