"""Linux platform backend.

MVP-stage stubs. Phase 3 fills in real implementations using
psutil + xdotool/wmctrl + D-Bus.
"""

from __future__ import annotations


def get_active_window_title() -> str | None:
    return None


def is_screen_sharing() -> bool:
    """Detect Zoom/Teams/screencast in progress. TODO: psutil + heuristics."""
    return False


def get_idle_seconds() -> float:
    """Seconds since last keyboard/mouse activity. TODO: xprintidle/xss."""
    return 0.0


def is_password_field_focused() -> bool:
    """Best-effort detection of password field. TODO: AT-SPI accessibility."""
    return False
