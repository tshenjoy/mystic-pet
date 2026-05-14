"""Windows platform backend — stub. Phase 5."""


def get_active_window_title():
    return None


def is_screen_sharing() -> bool:
    return False


def get_idle_seconds() -> float:
    return 0.0


def is_password_field_focused() -> bool:
    return False
