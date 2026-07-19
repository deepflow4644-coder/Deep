"""
fact_tracker.py

Handles reading and writing used_facts.json so that facts already
generated in the past are never generated again.

SETTING (change here if needed):
- TRACKER_FILE: path to the JSON file that stores past facts.
  Currently set to "used_facts.json" in the repo root.
"""

import json
import os

TRACKER_FILE = os.path.join(os.path.dirname(__file__), "..", "used_facts.json")


def load_used_facts():
    """Returns the list of facts already used (as plain strings)."""
    if not os.path.exists(TRACKER_FILE):
        return []
    with open(TRACKER_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("used_facts", [])


def save_used_fact(fact_text):
    """Appends a new fact to the tracker file and saves it."""
    used = load_used_facts()
    used.append(fact_text)
    with open(TRACKER_FILE, "w", encoding="utf-8") as f:
        json.dump({"used_facts": used}, f, ensure_ascii=False, indent=2)
