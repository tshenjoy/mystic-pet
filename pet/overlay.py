"""Transparent overlay window that displays the cat on screen."""

from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QTransform

from pet.state_machine import StateMachine, State, Direction
from pet.pet_widget import PetCat
from pet.sprite_renderer import SpriteRenderer
from pet.window_tracker import WindowTracker


class PetOverlay(QWidget):
    """Fullscreen transparent window. The cat is painted onto it each frame.

    - Cat walks along the top border of the active window
    - Hidden when the active window is maximized
    - Clicking the cat cycles its behavior
    """

    TICK_MS = 33  # ~30 fps

    def __init__(self, assets_dir):
        super().__init__()

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)

        self.renderer = SpriteRenderer(assets_dir)
        self.cat = PetCat(self.renderer)
        self.state_machine = StateMachine()
        self.window_tracker = WindowTracker()
        self._user_hidden = False  # True when user hides via tray

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(self.TICK_MS)

    def _tick(self):
        if self._user_hidden:
            return

        # Hide when active window is maximized
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

        self.cat.update(state, direction, win_rect, cursor_pos)

        # Reverse direction when cat hits window edge
        if self.cat.needs_direction_flip:
            self.state_machine.direction = (
                Direction.LEFT if direction == Direction.RIGHT else Direction.RIGHT
            )

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        anim = self.cat.animation_name(self.state_machine.state)
        frame = self.cat.get_current_frame(anim)

        if self.state_machine.direction.value < 0:
            frame = frame.transformed(QTransform().scale(-1, 1))

        painter.drawPixmap(self.cat.position, frame)
        painter.end()

    def mousePressEvent(self, event):
        """Click on cat = cycle behavior. Click elsewhere = pass through."""
        click_x = event.position().x()
        click_y = event.position().y()

        if self.cat.contains_point(int(click_x), int(click_y)):
            new_state = self.state_machine.on_click()
            self.update()
        else:
            # Let click pass to window below
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            QApplication.processEvents()
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

    def reload_sprites(self, custom_dir=None):
        """Reload sprites after recoloring."""
        self.renderer.reload_sprites(custom_dir)

    def set_user_hidden(self, hidden):
        """Called by system tray toggle."""
        self._user_hidden = hidden
        if hidden:
            self.hide()
        else:
            self.show()
