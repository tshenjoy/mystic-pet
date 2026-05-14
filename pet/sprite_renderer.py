"""Sprite renderer: load animation frames, return frame at index."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QMovie, QPixmap, QPainter, QColor


class SpriteRenderer:
    """Plays a single looping animation.

    MVP: one GIF for all states. Phase 2 swaps in per-state animations.
    Falls back to a placeholder pixmap when no asset is found, so the
    overlay can run before art is ready.
    """

    def __init__(self, assets_dir: Path, sprite_name: str = "idle.gif") -> None:
        self.assets_dir = Path(assets_dir)
        self.sprite_path = self.assets_dir / "pet" / sprite_name
        self.movie: QMovie | None = None
        self.placeholder: QPixmap | None = None
        self._load()

    def _load(self) -> None:
        if self.sprite_path.exists():
            self.movie = QMovie(str(self.sprite_path))
            self.movie.setCacheMode(QMovie.CacheMode.CacheAll)
        else:
            self.placeholder = self._make_placeholder()

    def _make_placeholder(self, size: int = 96) -> QPixmap:
        px = QPixmap(size, size)
        px.fill(Qt.GlobalColor.transparent)
        p = QPainter(px)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QColor(120, 90, 180, 220))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(8, 16, size - 16, size - 24)
        p.setBrush(QColor(60, 40, 100))
        p.drawPolygon(self._triangle(8, 16, 24, -10))
        p.drawPolygon(self._triangle(size - 32, 16, size - 8, -10))
        p.setBrush(QColor(255, 255, 255))
        p.drawEllipse(size // 2 - 18, size // 2 - 8, 12, 12)
        p.drawEllipse(size // 2 + 6, size // 2 - 8, 12, 12)
        p.setBrush(QColor(0, 0, 0))
        p.drawEllipse(size // 2 - 14, size // 2 - 4, 5, 5)
        p.drawEllipse(size // 2 + 10, size // 2 - 4, 5, 5)
        p.end()
        return px

    @staticmethod
    def _triangle(x1: int, y1: int, x2: int, y2: int):
        from PyQt6.QtGui import QPolygon
        from PyQt6.QtCore import QPoint
        return QPolygon([QPoint(x1, y1), QPoint(x2, y1), QPoint((x1 + x2) // 2, y2)])

    @property
    def frame_size(self) -> QSize:
        if self.movie:
            return self.movie.frameRect().size()
        if self.placeholder:
            return self.placeholder.size()
        return QSize(96, 96)

    def start(self) -> None:
        if self.movie:
            self.movie.start()

    def current_pixmap(self) -> QPixmap:
        if self.movie:
            return self.movie.currentPixmap()
        return self.placeholder
