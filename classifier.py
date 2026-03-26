"""
classifier.py
Auto-categorization and SLA priority assignment module

Core ITSM logic:
  - Keyword analysis  -> Category  (Network / Hardware / Software / General)
  - Condition-based   -> Priority  (P1 / P2 / P3 / P4)
"""

import re

# ── Category keyword dictionary ───────────────────────────────────────────────
CATEGORY_KEYWORDS = {
    "Network": [
        "network", "internet", "wifi", "wi-fi", "ethernet", "vpn",
        "dns", "ip", "ping", "firewall", "router", "switch", "bandwidth",
        "connection", "offline", "no internet", "latency", "packet loss",
    ],
    "Hardware": [
        "hardware", "monitor", "keyboard", "mouse", "printer", "scanner",
        "laptop", "desktop", "screen", "display", "ram", "memory",
        "hard drive", "ssd", "cpu", "fan", "power", "battery", "usb",
        "device", "blue screen", "bsod", "crash", "freeze", "overheat",
        "not responding", "unresponsive", "no display", "blank screen",
    ],
    "Software": [
        "software", "application", "app", "install", "uninstall", "update",
        "error", "bug", "license", "activation", "windows", "macos",
        "office", "excel", "outlook", "teams", "zoom", "browser", "chrome",
        "firefox", "antivirus", "login", "password", "reset", "driver",
    ],
}

# Device names that should always resolve to Hardware regardless of other matches
HARDWARE_DEVICES = ["printer", "monitor", "keyboard", "mouse", "scanner", "laptop", "desktop"]

# ── P1 trigger keywords (outage / multiple users affected) ────────────────────
P1_TRIGGER_KEYWORDS = [
    "all users", "everyone", "entire office", "whole company", "outage",
    "not working for everyone", "multiple users", "team cannot",
    "production", "server down", "service outage",
]

# ── P2 trigger keywords (single user fully blocked / security issue) ──────────
P2_TRIGGER_KEYWORDS = [
    "cannot work", "urgent", "asap", "critical", "blocked", "cannot access",
    "unable to login", "data loss", "lost data", "security", "breach",
]

# ── P4 trigger keywords (general requests / install inquiries) ────────────────
P4_TRIGGER_KEYWORDS = [
    "request", "would like", "please install", "can you install",
    "need new", "new software", "new application",
]


def classify_category(text: str) -> str:
    """
    Analyze ticket text and return the best-matching category.

    Rules:
      1. If a known device name is present, return 'Hardware' immediately.
      2. Otherwise score each category by keyword matches.
      3. Return the highest-scoring category; ties resolved by Network > Hardware > Software.
      4. If no keywords match, return 'General'.
    """
    text_lower = text.lower()

    # Rule 1: device name shortcut
    for device in HARDWARE_DEVICES:
        if re.search(r'\b' + re.escape(device) + r'\b', text_lower):
            return "Hardware"

    # Rule 2: keyword scoring
    scores = {cat: 0 for cat in CATEGORY_KEYWORDS}
    for category, keywords in CATEGORY_KEYWORDS.items():
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

    Priority levels:
      P1 (Critical) : Full service outage / multiple users affected
      P2 (High)     : Single user completely blocked / security issue
      P3 (Medium)   : Work impacted but workaround available
      P4 (Low)      : General request or inquiry
    """
    text_lower = text.lower()

    # P1 check
    for kw in P1_TRIGGER_KEYWORDS:
        if kw in text_lower:
            return "P1"

    # P2 check
    for kw in P2_TRIGGER_KEYWORDS:
        if kw in text_lower:
            return "P2"

    # P4 check — evaluated before category defaults to prevent false upgrades
    for kw in P4_TRIGGER_KEYWORDS:
        if kw in text_lower:
            return "P4"

    # Category-based defaults
    if category == "Network":
        return "P2"   # Network issues are high-impact by default

    if category in ("Hardware", "Software"):
        return "P3"

    return "P4"


def analyze_ticket(title: str, description: str) -> dict:
    """
    Run full analysis on a ticket title and description.
    Returns: { "category": str, "priority": str }
    """
    combined = f"{title} {description}"
    category = classify_category(combined)
    priority = assign_priority(combined, category)
    return {"category": category, "priority": priority}
