"""Tests for window tracker (Linux fallback path)."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pet.window_tracker import WindowTracker, WindowRect


def test_window_rect_properties():
    r = WindowRect(100, 50, 900, 650)
    assert r.width == 800
    assert r.height == 600
    assert r.left == 100
    assert r.top == 50


def test_default_rect():
    r = WindowRect()
    assert r.width == 800
    assert r.height == 600


def test_tracker_returns_rect_on_linux():
    t = WindowTracker()
    rect = t.get_active_window_rect()
    assert isinstance(rect, WindowRect)
    assert rect.width > 0


def test_cursor_returns_tuple_on_linux():
    t = WindowTracker()
    pos = t.get_cursor_position()
    assert isinstance(pos, tuple)
    assert len(pos) == 2


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
