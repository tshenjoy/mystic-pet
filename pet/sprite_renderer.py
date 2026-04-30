"""Sprite loading and frame management."""

import os
import json
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPolygon
from PyQt6.QtCore import Qt, QPoint


class SpriteRenderer:
    """Loads sprite frames from assets/ and provides the current frame.

    If no sprite images exist, draws colored placeholder rectangles
    so the app runs without art assets.
    """

    PLACEHOLDER_COLORS = {
        "idle": "#888888",
        "walk": "#4488CC",
        "stalk": "#CC8844",
        "chase": "#CC4444",
        "trash_can": "#44CC88",
    }

    def __init__(self, assets_dir, sprite_size=(64, 64)):
        self.assets_dir = assets_dir
        self.sprite_w, self.sprite_h = sprite_size
        self.frames = {}       # {"walk": [QPixmap, ...], "idle": [...]}
        self.metadata = {}     # loaded from metadata.json
        self._load_metadata()
        self._load_sprites()

    def _load_metadata(self):
        meta_path = os.path.join(self.assets_dir, "metadata.json")
        if os.path.exists(meta_path):
            with open(meta_path) as f:
                self.metadata = json.load(f)

    def _load_sprites(self):
        template_dir = os.path.join(self.assets_dir, "template")

        for anim_name in ["idle", "walk", "stalk", "chase", "trash_can"]:
            anim_dir = os.path.join(template_dir, anim_name)
            frames = []

            if os.path.isdir(anim_dir):
                files = sorted(f for f in os.listdir(anim_dir) if f.endswith(".png"))
                for fname in files:
                    px = QPixmap(os.path.join(anim_dir, fname))
                    if not px.isNull():
                        frames.append(px)

            if not frames:
                frames = self._make_placeholder_frames(anim_name)

            self.frames[anim_name] = frames

    def _make_placeholder_frames(self, anim_name, num_frames=4):
        """Generate simple colored rectangles as placeholder sprites."""
        color = QColor(self.PLACEHOLDER_COLORS.get(anim_name, "#AAAAAA"))
        frames = []

        for i in range(num_frames):
            px = QPixmap(self.sprite_w, self.sprite_h)
            px.fill(Qt.GlobalColor.transparent)
            painter = QPainter(px)

            # Slight vertical offset per frame to simulate bobbing
            bob = (i % 2) * 4
            painter.setBrush(color)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(4, 4 + bob, self.sprite_w - 8, self.sprite_h - 8, 8, 8)

            # Eyes
            painter.setBrush(QColor("white"))
            painter.drawEllipse(18, 14 + bob, 10, 10)
            painter.drawEllipse(36, 14 + bob, 10, 10)
            painter.setBrush(QColor("black"))
            painter.drawEllipse(21, 17 + bob, 5, 5)
            painter.drawEllipse(39, 17 + bob, 5, 5)

            # Ears (triangles)
            painter.setBrush(color.darker(130))
            ear_left = QPolygon([QPoint(12, 4 + bob), QPoint(6, 18 + bob), QPoint(22, 14 + bob)])
            ear_right = QPolygon([QPoint(52, 4 + bob), QPoint(42, 14 + bob), QPoint(58, 18 + bob)])
            painter.drawPolygon(ear_left)
            painter.drawPolygon(ear_right)

            painter.end()
            frames.append(px)

        return frames

    def get_frame(self, animation_name, frame_index):
        """Get a specific frame pixmap for an animation."""
        anim_frames = self.frames.get(animation_name, self.frames.get("idle", []))
        if not anim_frames:
            return QPixmap(self.sprite_w, self.sprite_h)
        return anim_frames[frame_index % len(anim_frames)]

    def frame_count(self, animation_name):
        return len(self.frames.get(animation_name, []))
