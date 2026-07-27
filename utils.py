# utils.py
# Small helper functions using Python's re (regex) module.
# Imported by other modules to keep input handling consistent.

import re


def clean_team_name(name: str) -> str:
    """
    Trim whitespace, remove special characters (keep letters/digits/spaces),
    and title-case the result so lookups are consistent.
    """
    name = name.strip()
    # Remove anything that isn't a letter, digit, or space
    name = re.sub(r"[^a-zA-Z0-9\s]", "", name)
    # Collapse multiple spaces into one and title-case
    name = re.sub(r"\s+", " ", name).title()
    return name


def validate_date(date_str: str) -> bool:
    """
    Return True if date_str matches the YYYY-MM-DD format, False otherwise.
    Does a simple regex check — doesn't verify calendar validity.
    """
    pattern = r"^\d{4}-\d{2}-\d{2}$"
    return bool(re.match(pattern, date_str))


def extract_score(text: str) -> str | None:
    """
    Pull the first 'N-N' score pattern out of a string and return it,
    or return None if no score is found.
    Example: "Final score: 2-1 after extra time" → "2-1"
    """
    match = re.search(r"\b(\d{1,2}-\d{1,2})\b", text)
    if match:
        return match.group(1)
    return None
