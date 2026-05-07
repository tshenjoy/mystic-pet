"""Transparent overlay window that displays the cat on screen."""

import sys

from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QTimer, QRect
from PyQt6.QtGui import QPainter

from pet.state_machine import StateMachine, State, Direction
from pet.pet_widget import PetCat
from pet.sprite_renderer import SpriteRenderer
from pet.window_tracker import WindowTracker


class PetOverlay(QWidget):
    """Fullscreen transparent window. The cat is painted onto it each frame."""

    TICK_MS = 33  # ~30 fps

    def __init__(self, assets_dir):
        super().__init__()

        self._is_macos = sys.platform == "darwin"

        if self._is_macos:
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint
                | Qt.WindowType.NoDropShadowWindowHint
            )
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        else:
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint
                | Qt.WindowType.WindowStaysOnTopHint
                | Qt.WindowType.Tool
            )
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Don't set geometry here - will be set in _tick based on cat position
        # Start with minimal geometry to avoid fullscreen issues
        self.setGeometry(0, 0, 1, 1)

        self.renderer = SpriteRenderer(assets_dir)
        self.cat = PetCat(self.renderer)
        self.state_machine = StateMachine()
        self.window_tracker = WindowTracker()
        self._user_hidden = False
        self._last_cat_rect = QRect()
        self._macos_monitor = None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(self.TICK_MS)

    def showEvent(self, event):
        super().showEvent(event)
        # Apply macOS settings after window is fully created
        if self._is_macos and not self._macos_monitor:
            # Small delay to ensure window handle is ready
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(100, self._init_macos)

    def _init_macos(self):
        """Initialize macOS-specific settings after window is ready."""
        self._apply_macos_ignore_mouse()
        self._setup_macos_click_monitor()

    def _apply_macos_ignore_mouse(self):
        """Make the native NSWindow ignore all mouse events and not become key window."""
        try:
            ns_window = self._get_ns_window()
            if ns_window:
                import AppKit
                # Ignore mouse events - clicks pass through to windows below
                ns_window.setIgnoresMouseEvents_(True)
                # Prevent window from becoming key/main window
                ns_window.setCanBecomeKeyWindow_(False)
                ns_window.setCanBecomeMainWindow_(False)
                # Set to floating window level - above normal windows
                ns_window.setLevel_(AppKit.NSFloatingWindowLevel)
                # Collection behavior for Stage Manager compatibility
                try:
                    ns_window.setCollectionBehavior_(
                        AppKit.NSWindowCollectionBehaviorCanJoinAllSpaces
                    )
                except Exception:
                    pass
        except Exception:
            pass

    def _get_ns_window(self):
        """Get the native NSWindow."""
        try:
            qwindow = self.window().windowHandle()
            if qwindow:
                import objc
                import AppKit
                ptr = qwindow.winId()
                ns_window = objc.objc_object(c_void_p=ptr)
                return ns_window
        except Exception:
            pass
        return None

    def _setup_macos_click_monitor(self):
        """Use CGEventTap to listen for clicks on the cat without intercepting them."""
        if self._macos_monitor is not None:
            return
        try:
            import Quartz
            import CoreFoundation

            def tap_callback(proxy, type_, event, refcon):
                # Only handle left mouse down
                if type_ != Quartz.kCGEventLeftMouseDown:
                    return event

                loc = Quartz.CGEventGetLocation(event)
                x = int(loc.x)
                y = int(loc.y)

                # Convert macOS bottom-left coordinates to top-left
                try:
                    screen_h = Quartz.CGDisplayBounds(Quartz.CGMainDisplayID()).size.height
                    y = int(screen_h) - y
                except Exception:
                    pass

                if self.cat.contains_point(x, y):
                    # Click is on the cat - trigger action
                    self.state_machine.on_click()
                    # Schedule update on main thread
                    CoreFoundation.CFRunLoopPerformBlock(
                        CoreFoundation.CFRunLoopGetMain(),
                        CoreFoundation.kCFRunLoopDefaultMode,
                        lambda: self.update()
                    )

                # Always return the event unchanged - don't intercept
                return event

            tap = Quartz.CGEventTapCreate(
                Quartz.kCGSessionEventTap,
                Quartz.kCGHeadInsertEventTap,
                Quartz.kCGEventTapOptionListenOnly,  # Listen only - never intercepts
                Quartz.CGEventMaskBit(Quartz.kCGEventLeftMouseDown),
                tap_callback,
                None
            )
            if tap:
                run_loop_source = Quartz.CFMachPortCreateRunLoopSource(None, tap, 0)
                Quartz.CFRunLoopAddSource(
                    Quartz.CFRunLoopGetCurrent(),
                    run_loop_source,
                    Quartz.kCFRunLoopCommonModes
                )
                Quartz.CGEventTapEnable(tap, True)
                self._macos_monitor = tap
        except Exception as e:
            print(f"Failed to setup click monitor: {e}")
            pass

    def _tick(self):
        if self._user_hidden:
            return

        if self.window_tracker.is_maximized():
            if self.isVisible():
                self.hide()
            return
        else:
            if not self.isVisible():
                self.show()

        win_rect = self.window_tracker.get_active_window_rect()
        cursor_pos = self.window_tracker.get_cursor_position()

        dist = self.cat.cursor_distance(cursor_pos)
        state = self.state_machine.update(cursor_distance=dist)
        direction = self.state_machine.direction

        # Apply direction flip BEFORE updating cat position to avoid 1-frame desync
        if self.cat.needs_direction_flip:
            self.state_machine.direction = (
                Direction.LEFT if direction == Direction.RIGHT else Direction.RIGHT
            )
            direction = self.state_machine.direction

        self.cat.update(state, direction, win_rect, cursor_pos)

        # Position window to exactly cover the cat (not fullscreen)
        # This prevents the window from interfering with other apps
        self.setGeometry(self.cat.x, self.cat.y, self.cat.display_w, self.cat.display_h)

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        anim = self.cat.animation_name(self.state_machine.state)
        # Sprites face LEFT by default, so flip when moving RIGHT
        flipped = self.state_machine.direction.value > 0
        frame = self.cat.get_current_frame(anim, flipped=flipped)

        # Draw at (0,0) because window is positioned at cat's location
        target = QRect(0, 0, self.cat.display_w, self.cat.display_h)
        painter.drawPixmap(target, frame)
        painter.end()

    def reload_sprites(self, custom_dir=None):
        self.renderer.reload_sprites(custom_dir)

    def set_user_hidden(self, hidden):
        self._user_hidden = hidden
        if hidden:
            self.hide()
        else:
            self.show()
