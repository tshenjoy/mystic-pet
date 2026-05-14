"""Settings: load defaults, layer user overrides, save mutations."""

from __future__ import annotations

import os
from copy import deepcopy
from pathlib import Path

import yaml

_DEFAULT_PATH = Path(__file__).parent / "default_settings.yaml"
_USER_PATH = Path.home() / ".config" / "mystic-pet" / "settings.yaml"


def _deep_merge(base: dict, override: dict) -> dict:
    out = deepcopy(base)
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def load() -> dict:
    with open(_DEFAULT_PATH) as f:
        defaults = yaml.safe_load(f)
    if _USER_PATH.exists():
        with open(_USER_PATH) as f:
            user = yaml.safe_load(f) or {}
        return _deep_merge(defaults, user)
    return defaults


def save(settings: dict) -> None:
    _USER_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_USER_PATH, "w") as f:
        yaml.safe_dump(settings, f, sort_keys=False)
