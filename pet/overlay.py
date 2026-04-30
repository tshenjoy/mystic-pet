"""Transparent overlay window that displays the cat on screen."""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QTimer, QRect
from PyQt6.QtGui import QPainter, QTransform

from pet.state_machine import StateMachine, State
from pet.pet_widget import PetCat
from pet.sprite_renderer import SpriteRenderer
from pet.window_tracker import WindowTracker


class PetOverlay(QWidget):
    """Fullscreen transparent window. The cat is painted onto it each frame."""

    TICK_MS = 33  # ~30 fps

    def __init__(self, assets_dir):
        super().__init__()

        # Transparent, always-on-top, click-through window
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool                    # hide from taskbar
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Cover entire screen
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)

        # Core components
        self.renderer = SpriteRenderer(assets_dir)
        self.cat = PetCat(self.renderer)
        self.state_machine = StateMachine()
        self.window_tracker = WindowTracker()

        # Main loop timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(self.TICK_MS)

    def _tick(self):
        """Main update loop — runs every TICK_MS."""
        # Get active window and cursor
        win_rect = self.window_tracker.get_active_window_rect()
        cursor_pos = self.window_tracker.get_cursor_position()

        # Update state machine
        dist = self.cat.cursor_distance(cursor_pos)
        state = self.state_machine.update(cursor_distance=dist)
        direction = self.state_machine.direction

        # Update cat position and animation
        self.cat.update(state, direction, win_rect, cursor_pos)

        # Repaint
        self.update()

    def paintEvent(self, event):
        """Draw the cat sprite at its current position."""
        painter = QPainter(self)
        anim = self.cat.animation_name(self.state_machine.state)
        frame = self.cat.get_current_frame(anim)

        # Flip sprite horizontally when facing left
        if self.state_machine.direction.value < 0:
            frame = frame.transformed(QTransform().scale(-1, 1))

        painter.drawPixmap(self.cat.position, frame)
        painter.end()
