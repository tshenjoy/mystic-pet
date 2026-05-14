"""PetWidget: paints the current sprite frame and dispatches input events."""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QMouseEvent, QPainter
from PyQt6.QtWidgets import QWidget

from pet.sprite_renderer import SpriteRenderer


class PetWidget(QWidget):
    clicked = pyqtSignal()
    drag_finished = pyqtSignal(int, int)  # new (x, y) of the parent overlay

    def __init__(self, renderer: SpriteRenderer, parent=None) -> None:
        super().__init__(parent)
        self.renderer = renderer
        size = renderer.frame_size
        self.setFixedSize(size)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self._drag_origin = None
        self._press_pos = None

    def paintEvent(self, _event) -> None:
        p = QPainter(self)
        p.drawPixmap(0, 0, self.renderer.current_pixmap())

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self._press_pos = event.globalPosition().toPoint()
            self._drag_origin = self.window().pos()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._press_pos is None:
            return
        delta = event.globalPosition().toPoint() - self._press_pos
        self.window().move(self._drag_origin + delta)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() != Qt.MouseButton.LeftButton:
            return
        moved = (event.globalPosition().toPoint() - self._press_pos).manhattanLength() if self._press_pos else 0
        self._press_pos = None
        if moved < 5:
            self.clicked.emit()
        else:
            pos = self.window().pos()
            self.drag_finished.emit(pos.x(), pos.y())
