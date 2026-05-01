"""Transparent overlay window that displays the cat on screen."""

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
        self._user_hidden = False
        self._last_cat_rect = QRect()

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

        # Only repaint the area where the cat was and is now
        new_rect = QRect(self.cat.x, self.cat.y, self.cat.display_w, self.cat.display_h)
        dirty = self._last_cat_rect.united(new_rect).adjusted(-2, -2, 2, 2)
        self._last_cat_rect = new_rect
        self.update(dirty)

    def paintEvent(self, event):
        painter = QPainter(self)
        anim = self.cat.animation_name(self.state_machine.state)
        flipped = self.state_machine.direction.value < 0
        frame = self.cat.get_current_frame(anim, flipped=flipped)

        target = QRect(self.cat.x, self.cat.y, self.cat.display_w, self.cat.display_h)
        painter.drawPixmap(target, frame)
        painter.end()

    def mousePressEvent(self, event):
        click_x = int(event.position().x())
        click_y = int(event.position().y())

        if self.cat.contains_point(click_x, click_y):
            self.state_machine.on_click()
            self.update()
        else:
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            QApplication.processEvents()
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

    def reload_sprites(self, custom_dir=None):
        self.renderer.reload_sprites(custom_dir)

    def set_user_hidden(self, hidden):
        self._user_hidden = hidden
        if hidden:
            self.hide()
        else:
            self.show()
