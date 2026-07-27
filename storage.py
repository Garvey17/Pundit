# storage.py
# Functions for reading and writing the app's single local data file (data.json).
# Using JSON keeps things simple and human-readable.

import json
import os

DATA_FILE = "data.json"

# Default empty structure — used when the file is missing or unreadable
DEFAULT_DATA = {
    "favourites": [],
    "notes": {},
    "cached_summaries": {},
}


def load_data() -> dict:
    """
    Read data.json and return its contents as a dict.
    If the file doesn't exist or is corrupted, return the default empty structure
    so the app never crashes on startup.
    """
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Make sure all expected keys are present (handles partial/old files)
        for key in DEFAULT_DATA:
            if key not in data:
                data[key] = DEFAULT_DATA[key]
        return data
    except (FileNotFoundError, json.JSONDecodeError):
        # File missing or corrupted — start fresh
        return dict(DEFAULT_DATA)


def save_data(data: dict) -> None:
    """
    Write the data dict to data.json.
    indent=2 keeps the file human-readable when opened in a text editor.
    """
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except OSError as e:
        # If we can't write (e.g. permission issue), print a warning but don't crash
        print(f"Warning: could not save data — {e}")
