# Sports Match Analyzer & Fan Companion

A sports companion app that lets you look up football teams, view upcoming fixtures and past results, generate AI-written previews and trivia via Gemini, bookmark favourite teams, and save personal notes — all stored locally in a single `data.json` file.

The application includes **two complete front-end interfaces** that reuse the exact same modular Python backend logic:
1. **Web UI** built with **Streamlit** ([app.py](file:///c:/Users/USER/Downloads/Pundit/app.py))
2. **Desktop Desktop GUI** built with **Tkinter** ([gui_app.py](file:///c:/Users/USER/Downloads/Pundit/gui_app.py))

---

## Prerequisites

- Python 3.10 or later
- A **Gemini API key** (free tier works fine)
- No TheSportsDB API key required — the free public v1 tier is used automatically

---

## Setup

### 1. Navigate to the project directory

```bash
cd path/to/Pundit
```

### 2. Create and activate a virtual environment (recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set your Gemini API key

The app reads the key from the `GEMINI_API_KEY` environment variable.

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY = "your-key-here"
```

**Windows (Command Prompt):**
```cmd
set GEMINI_API_KEY=your-key-here
```

**macOS / Linux:**
```bash
export GEMINI_API_KEY="your-key-here"
```

> Get a free Gemini API key at https://aistudio.google.com/app/apikey

---

## Running the App

### Option A: Streamlit Web UI (Default)

```bash
streamlit run app.py
```
The app will open automatically in your browser at `http://localhost:8501`.

### Option B: Tkinter Desktop GUI (Alternative)

```bash
python gui_app.py
```
This launches a native desktop application window using Python's built-in `tkinter` and `ttk`.

---

## Data file

All bookmarks, notes, and cached AI summaries are saved to **`data.json`** in the project root. This file is created automatically on first run and shared seamlessly between both the Streamlit web app and Tkinter desktop app.

---

## File overview

| File | Purpose |
|------|---------|
| `app.py` | Streamlit Web UI — main web entry point |
| `gui_app.py` | Tkinter Desktop GUI — alternative native window interface |
| `models.py` | `Team` and `Match` data classes |
| `api_client.py` | TheSportsDB API wrapper |
| `analyzer.py` | Win/draw/loss predictor + Gemini text generation |
| `storage.py` | `load_data()` / `save_data()` for `data.json` |
| `utils.py` | Regex helpers: clean names, validate dates, extract scores |
| `requirements.txt` | Python package dependencies |
| `data.json` | Auto-created local storage |
