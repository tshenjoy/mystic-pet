"""Track the currently active window's position and size (Windows only)."""

import sys

if sys.platform == "win32":
    import win32gui
    import win32con


class WindowRect:
    """Simple rectangle representing a window's position and size."""

    def __init__(self, left=0, top=0, right=800, bottom=600):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    @property
    def width(self):
        return self.right - self.left

    @property
    def height(self):
        return self.bottom - self.top

    def __repr__(self):
        return f"WindowRect(left={self.left}, top={self.top}, w={self.width}, h={self.height})"


class WindowTracker:
    """Polls the foreground window and returns its rect.

    On Linux, returns a default rect (for dev testing only).
    """

    def __init__(self):
        self._last_rect = WindowRect()
        self._last_maximized = False
        self._is_windows = sys.platform == "win32"

    def get_active_window_rect(self):
        """Returns WindowRect of the currently active window."""
        if not self._is_windows:
            return self._last_rect

        try:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                self._last_rect = WindowRect(left, top, right, bottom)
        except Exception:
            pass

        return self._last_rect

    def is_maximized(self):
        """Check if the active window is maximized."""
        if not self._is_windows:
            return self._last_maximized

        try:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                placement = win32gui.GetWindowPlacement(hwnd)
                self._last_maximized = (placement[1] == win32con.SW_SHOWMAXIMIZED)
        except Exception:
            pass

        return self._last_maximized

    def get_cursor_position(self):
        """Returns (x, y) of mouse cursor."""
        if not self._is_windows:
            return (0, 0)

        try:
            import win32api
            return win32api.GetCursorPos()
        except Exception:
            return (0, 0)
