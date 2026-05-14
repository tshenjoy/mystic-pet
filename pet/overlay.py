"""Transparent overlay window that displays the cat on screen."""

import sys
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QBitmap

from pet.state_machine import StateMachine, State, Direction
from pet.pet_widget import PetCat
from pet.sprite_renderer import SpriteRenderer
from pet.window_tracker import WindowTracker


class PetOverlay(QWidget):
    """Cat-sized window that follows the pet's position each frame.

    Uses setMask() to cut out the sprite shape so it works
    on X11 without a compositor (no WA_TranslucentBackground needed).
    """

    TICK_MS = 33  # ~30 fps

    def __init__(self, assets_dir):
        super().__init__()

        flags = (
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        if sys.platform.startswith("linux"):
            flags |= Qt.WindowType.X11BypassWindowManagerHint
        self.setWindowFlags(flags)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.renderer = SpriteRenderer(assets_dir)
        self.cat = PetCat(self.renderer)
        self.state_machine = StateMachine()
        self.window_tracker = WindowTracker()
        self._user_hidden = False
        self._current_frame = None

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(self.TICK_MS)

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

        self.cat.update(state, direction, win_rect, cursor_pos)

        if self.cat.needs_direction_flip:
            self.state_machine.direction = (
                Direction.LEFT if direction == Direction.RIGHT else Direction.RIGHT
            )

        anim = self.cat.animation_name(self.state_machine.state)
        flipped = direction.value < 0
        self._current_frame = self.cat.get_current_frame(anim, flipped=flipped)

        scaled = self._current_frame.scaled(self.cat.display_w, self.cat.display_h)
        mask = scaled.createMaskFromColor(Qt.GlobalColor.transparent, Qt.MaskMode.MaskInColor)
        self.setMask(mask)

        self.setFixedSize(self.cat.display_w, self.cat.display_h)
        self.move(self.cat.x, self.cat.y)
        self.update()

    def paintEvent(self, event):
        if self._current_frame is None:
            return
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.cat.display_w, self.cat.display_h, self._current_frame)
        painter.end()

    def mousePressEvent(self, event):
        self.state_machine.on_click()
        self.update()

    def reload_sprites(self, custom_dir=None):
        self.renderer.reload_sprites(custom_dir)

    def set_user_hidden(self, hidden):
        self._user_hidden = hidden
        if hidden:
            self.hide()
        else:
            self.show()
