"""User settings with JSON persistence."""

import os
import json


DEFAULTS = {
    "pet_size": 64,
    "walk_speed": 2,
    "chase_speed": 4,
    "animation_fps": 10,
    "custom_sprite_path": None,
}


class Settings:
    """Simple key-value settings backed by a JSON file."""

    def __init__(self, config_dir=None):
        if config_dir is None:
            config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")
        self.path = os.path.join(config_dir, "user_settings.json")
        self.data = dict(DEFAULTS)
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path) as f:
                saved = json.load(f)
            self.data.update(saved)

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=2)

    def get(self, key):
        return self.data.get(key, DEFAULTS.get(key))

    def set(self, key, value):
        self.data[key] = value
        self.save()
