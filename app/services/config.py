"""
app/services/config.py
Central configuration loader.

Reads config.json once at import time and exposes typed accessors.
All modules import from here — never read config.json directly.

Usage:
    from app.services.config import get_server_config, get_classifier_config, get_ticket_config
"""

import json
import os

_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "config.json")
_config: dict = {}


def _load() -> dict:
    """Load and return the full config.json. Raises on missing or malformed file."""
    path = os.path.normpath(_CONFIG_PATH)
    if not os.path.exists(path):
        raise FileNotFoundError(f"config.json not found at: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _get_config() -> dict:
    """Return the cached config, loading it on first access."""
    global _config
    if not _config:
        _config = _load()
    return _config


def get_server_config() -> dict:
    """
    Returns server settings.
    Example: { "host": "0.0.0.0", "port": 5000, "debug": false }
    """
    return _get_config()["server"]


def get_classifier_config() -> dict:
    """
    Returns the full classifier section:
      - hardware_devices
      - category_keywords
      - priority_keywords
      - category_priority_defaults
    """
    return _get_config()["classifier"]


def get_ticket_config() -> dict:
    """
    Returns ticket settings.
    Example: { "valid_statuses": [...], "valid_priorities": [...] }
    """
    return _get_config()["ticket"]