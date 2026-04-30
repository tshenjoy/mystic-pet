"""Tests for settings persistence."""

import sys
import os
import tempfile
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config.settings import Settings, DEFAULTS


def test_defaults_loaded():
    with tempfile.TemporaryDirectory() as tmpdir:
        s = Settings(config_dir=tmpdir)
        assert s.get("pet_size") == 64
        assert s.get("walk_speed") == 2
        assert s.get("custom_sprite_path") is None


def test_set_and_persist():
    with tempfile.TemporaryDirectory() as tmpdir:
        s = Settings(config_dir=tmpdir)
        s.set("pet_size", 128)
        assert s.get("pet_size") == 128

        # Reload from disk
        s2 = Settings(config_dir=tmpdir)
        assert s2.get("pet_size") == 128


def test_unknown_key_returns_none():
    with tempfile.TemporaryDirectory() as tmpdir:
        s = Settings(config_dir=tmpdir)
        assert s.get("nonexistent_key") is None


def test_save_creates_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        s = Settings(config_dir=tmpdir)
        s.set("walk_speed", 5)
        path = os.path.join(tmpdir, "user_settings.json")
        assert os.path.exists(path)
        with open(path) as f:
            data = json.load(f)
        assert data["walk_speed"] == 5


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    passed = 0
    for test in tests:
        try:
            test()
            print(f"  PASS  {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL  {test.__name__}: {e}")
        except Exception as e:
            print(f"  ERROR {test.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} passed")
