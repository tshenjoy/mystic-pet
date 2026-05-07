"""Track the currently active window's position and size."""

import sys
import subprocess


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


if sys.platform == "win32":
    import win32gui
    import win32con


class WindowTracker:
    """Polls the foreground window and returns its rect."""

    def __init__(self):
        self._last_rect = WindowRect()
        self._last_maximized = False
        self._is_windows = sys.platform == "win32"
        self._is_linux = sys.platform.startswith("linux")
        self._is_macos = sys.platform == "darwin"
        self._active_wid = None

    def get_active_window_rect(self):
        if self._is_windows:
            return self._get_rect_windows()
        elif self._is_linux:
            return self._get_rect_linux()
        elif self._is_macos:
            return self._get_rect_macos()
        return self._last_rect

    def is_maximized(self):
        if self._is_windows:
            return self._is_maximized_windows()
        elif self._is_linux:
            return self._is_maximized_linux()
        elif self._is_macos:
            return self._is_maximized_macos()
        return self._last_maximized

    def get_cursor_position(self):
        if self._is_windows:
            return self._get_cursor_windows()
        elif self._is_linux:
            return self._get_cursor_linux()
        elif self._is_macos:
            return self._get_cursor_macos()
        return (0, 0)

    # --- Windows ---

    def _get_rect_windows(self):
        try:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                self._last_rect = WindowRect(left, top, right, bottom)
        except Exception:
            pass
        return self._last_rect

    def _is_maximized_windows(self):
        try:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                placement = win32gui.GetWindowPlacement(hwnd)
                self._last_maximized = (placement[1] == win32con.SW_SHOWMAXIMIZED)
        except Exception:
            pass
        return self._last_maximized

    def _get_cursor_windows(self):
        try:
            import win32api
            return win32api.GetCursorPos()
        except Exception:
            return (0, 0)

    # --- Linux (X11 via xdotool/xprop) ---

    def _get_rect_linux(self):
        try:
            out = subprocess.run(
                ["xdotool", "getactivewindow", "getwindowgeometry", "--shell"],
                capture_output=True, text=True, timeout=1
            )
            if out.returncode != 0:
                return self._last_rect

            vals = {}
            for line in out.stdout.strip().split("\n"):
                if "=" in line:
                    k, v = line.split("=", 1)
                    vals[k] = v

            self._active_wid = vals.get("WINDOW")
            x = int(vals.get("X", 0))
            y = int(vals.get("Y", 0))
            w = int(vals.get("WIDTH", 800))
            h = int(vals.get("HEIGHT", 600))
            self._last_rect = WindowRect(x, y, x + w, y + h)
        except Exception:
            pass
        return self._last_rect

    def _is_maximized_linux(self):
        wid = self._active_wid
        if not wid:
            return self._last_maximized
        try:
            out = subprocess.run(
                ["xprop", "-id", str(wid), "_NET_WM_STATE"],
                capture_output=True, text=True, timeout=1
            )
            if out.returncode == 0:
                self._last_maximized = (
                    "_NET_WM_STATE_MAXIMIZED_VERT" in out.stdout
                    and "_NET_WM_STATE_MAXIMIZED_HORZ" in out.stdout
                )
        except Exception:
            pass
        return self._last_maximized

    def _get_cursor_linux(self):
        try:
            out = subprocess.run(
                ["xdotool", "getmouselocation"],
                capture_output=True, text=True, timeout=1
            )
            if out.returncode != 0:
                return (0, 0)
            parts = out.stdout.strip().split()
            x = int(parts[0].split(":")[1])
            y = int(parts[1].split(":")[1])
            return (x, y)
        except Exception:
            return (0, 0)

    # --- macOS (Quartz/AppKit via pyobjc) ---

    def _macos_screen_height(self):
        try:
            from Quartz import CGMainDisplayID, CGDisplayBounds
            bounds = CGDisplayBounds(CGMainDisplayID())
            return int(bounds.size.height)
        except Exception:
            return 0

    def _get_rect_macos(self):
        # Try AXUIElement (Accessibility API) first
        rect = self._get_rect_macos_ax()
        if rect:
            return rect
        # Fallback to Quartz bounds
        return self._get_rect_macos_quartz()

    def _get_rect_macos_ax(self):
        """Use Accessibility API - returns top-left coordinates."""
        try:
            import ApplicationServices
            from AppKit import NSWorkspace

            front_app = NSWorkspace.sharedWorkspace().frontmostApplication()
            if not front_app:
                return None

            front_pid = front_app.processIdentifier()
            app_element = ApplicationServices.AXUIElementCreateApplication(front_pid)

            value_ref = ApplicationServices.AXUIElementCopyAttributeValue(
                app_element,
                ApplicationServices.kAXFocusedWindowAttribute,
                None
            )
            if value_ref is None or value_ref[0] is None:
                return None

            window_element = value_ref[0]

            pos_ref = ApplicationServices.AXUIElementCopyAttributeValue(
                window_element,
                ApplicationServices.kAXPositionAttribute,
                None
            )
            size_ref = ApplicationServices.AXUIElementCopyAttributeValue(
                window_element,
                ApplicationServices.kAXSizeAttribute,
                None
            )

            if pos_ref is None or size_ref is None:
                return None
            if pos_ref[0] is None or size_ref[0] is None:
                return None

            pos = pos_ref[0]
            size = size_ref[0]

            # AX API uses BOTTOM-LEFT origin (same as Quartz)
            # pos.y = distance from screen bottom to BOTTOM of window
            # So: window top in top-left coords = screen_h - (pos.y + size.height)

            x = int(pos.x)
            y = int(pos.y)
            w = int(size.width)
            h = int(size.height)

            if w <= 0 or h <= 0:
                return None

            screen_h = self._macos_screen_height()
            if screen_h:
                top = screen_h - (y + h)
            else:
                top = y

            print(f"DEBUG AX: x={x}, y={y}, w={w}, h={h}, screen_h={screen_h}, top={top}")

            self._last_rect = WindowRect(x, top, x + w, top + h)
            return self._last_rect
        except Exception as e:
            print(f"DEBUG AX Error: {e}")
            return None

    def _get_rect_macos_quartz(self):
        """Use Quartz window list to get bounds."""
        try:
            from AppKit import NSWorkspace
            from Quartz import CGWindowListCopyWindowInfo, kCGWindowListOptionOnScreenOnly, kCGNullWindowID

            front_app = NSWorkspace.sharedWorkspace().frontmostApplication()
            if not front_app:
                return self._last_rect

            front_pid = front_app.processIdentifier()
            windows = CGWindowListCopyWindowInfo(kCGWindowListOptionOnScreenOnly, kCGNullWindowID)
            best = None
            best_area = -1
            for win in windows:
                if win.get("kCGWindowOwnerPID") != front_pid:
                    continue
                if win.get("kCGWindowLayer", 0) != 0:
                    continue
                bounds = win.get("kCGWindowBounds") or {}
                w = int(bounds.get("Width", 0))
                h = int(bounds.get("Height", 0))
                if w <= 0 or h <= 0:
                    continue
                area = w * h
                if area > best_area:
                    best_area = area
                    best = bounds

            if not best:
                return self._last_rect

            x = int(best.get("X", 0))
            y = int(best.get("Y", 0))
            w = int(best.get("Width", 0))
            h = int(best.get("Height", 0))

            screen_h = self._macos_screen_height()

            # Quartz uses BOTTOM-LEFT origin
            # kCGWindowBounds.Y = distance from screen bottom to BOTTOM of window
            # Window top in Quartz = y + h
            # Convert to top-left: top = screen_h - (y + h)

            top = screen_h - (y + h) if screen_h else y

            print(f"DEBUG Quartz: x={x}, y={y}, w={w}, h={h}, screen_h={screen_h}, top={top}")

            self._last_rect = WindowRect(x, top, x + w, top + h)
        except Exception as e:
            print(f"DEBUG Quartz Error: {e}")
            pass
        return self._last_rect

    def _is_maximized_macos(self):
        try:
            from Quartz import CGMainDisplayID, CGDisplayBounds
            bounds = CGDisplayBounds(CGMainDisplayID())
            screen_w = int(bounds.size.width)
            screen_h = int(bounds.size.height)
            rect = self._last_rect
            tol = 2
            self._last_maximized = (
                abs(rect.width - screen_w) <= tol and abs(rect.height - screen_h) <= tol
            )
        except Exception:
            pass
        return self._last_maximized

    def _get_cursor_macos(self):
        try:
            from Quartz import CGEventCreate, CGEventGetLocation
            event = CGEventCreate(None)
            loc = CGEventGetLocation(event)
            x = int(loc.x)
            y = int(loc.y)
            screen_h = self._macos_screen_height()
            if screen_h:
                return (x, screen_h - y)
            return (x, y)
        except Exception:
            return (0, 0)
