"""
app/services/classifier.py
Auto-categorization and SLA priority assignment module.

All keywords and priority defaults are loaded from config.json —
no code changes needed to tune classification behavior.

Core ITSM logic:
  - Keyword analysis  -> Category  (Network / Hardware / Software / General)
  - Condition-based   -> Priority  (P1 / P2 / P3 / P4)
"""

import re
from app.services.config import get_classifier_config


def _cfg():
    """Shorthand accessor — returns the classifier config section."""
    return get_classifier_config()


def classify_category(text: str) -> str:
    """
    Analyze ticket text and return the best-matching category.

    Rules:
      1. If a known device name is present, return 'Hardware' immediately.
      2. Otherwise score each category by keyword matches.
      3. Return the highest-scoring category.
      4. If no keywords match, return 'General'.
    """
    cfg = _cfg()
    text_lower = text.lower()

    # Rule 1: device name shortcut — loaded from config
    for device in cfg["hardware_devices"]:
        if re.search(r'\b' + re.escape(device) + r'\b', text_lower):
            return "Hardware"

    # Rule 2: keyword scoring — loaded from config
    scores = {cat: 0 for cat in cfg["category_keywords"]}
    for category, keywords in cfg["category_keywords"].items():
        for kw in keywords:
            if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                scores[category] += 1

    best_category = max(scores, key=scores.get)
    if scores[best_category] == 0:
        return "General"
    return best_category


def assign_priority(text: str, category: str) -> str:
    """
    Determine SLA priority based on ticket content and category.

    Keyword order (evaluated top to bottom):
      P1 keywords → P2 keywords → P4 keywords → category defaults

    All keywords and defaults are loaded from config.json.
    """
    cfg = _cfg()
    text_lower = text.lower()
    priority_keywords = cfg["priority_keywords"]

    # Explicit keyword checks in priority order: P1 → P2 → P4
    for priority in ["P1", "P2", "P4"]:
        for kw in priority_keywords.get(priority, []):
            if kw in text_lower:
                return priority

    # Fall back to category-based default
    return cfg["category_priority_defaults"].get(category, "P4")


def analyze_ticket(title: str, description: str) -> dict:
    """
    Run full analysis on a ticket title and description.
    Returns: { "category": str, "priority": str }
    """
    combined = f"{title} {description}"
    category = classify_category(combined)
    priority = assign_priority(combined, category)
    return {"category": category, "priority": priority}