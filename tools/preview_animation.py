"""Preview sprite animations for the desktop pet."""

import argparse
import os
import sys

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from pet.sprite_renderer import SpriteRenderer, ANIMATION_NAMES


class PreviewWindow(QMainWindow):
    def __init__(self, assets_dir, custom_dir=None, fps=10, scale=1.0, anim="walk", flipped=False):
        super().__init__()
        self.setWindowTitle("Desktop Pet Animation Preview")

        self.assets_dir = assets_dir
        self.custom_dir = custom_dir
        self.renderer = SpriteRenderer(self.assets_dir)
        if self.custom_dir:
            self.renderer.reload_sprites(self.custom_dir)

        self.animations = [a for a in ANIMATION_NAMES if self.renderer.frame_count(a) > 0]
        if not self.animations:
            self.animations = ANIMATION_NAMES[:]

        self.current_anim = anim if anim in self.animations else self.animations[0]
        self.frame_index = 0
        self.playing = True
        self.flipped = flipped

        self.timer = QTimer(self)
        self.timer.timeout.connect(self._advance_frame)

        self._build_ui(fps, scale)
        self._set_fps(fps)
        self._render_frame()

    def _build_ui(self, fps, scale):
        root = QWidget()
        self.setCentralWidget(root)

        layout = QVBoxLayout(root)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        controls = QHBoxLayout()
        controls.setSpacing(8)

        self.anim_combo = QComboBox()
        self.anim_combo.addItems(self.animations)
        self.anim_combo.setCurrentText(self.current_anim)
        self.anim_combo.currentTextChanged.connect(self._change_anim)
        controls.addWidget(QLabel("Anim"))
        controls.addWidget(self.anim_combo)

        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(1, 60)
        self.fps_spin.setValue(fps)
        self.fps_spin.valueChanged.connect(self._set_fps)
        controls.addWidget(QLabel("FPS"))
        controls.addWidget(self.fps_spin)

        self.scale_spin = QDoubleSpinBox()
        self.scale_spin.setRange(0.1, 4.0)
        self.scale_spin.setSingleStep(0.1)
        self.scale_spin.setValue(scale)
        self.scale_spin.valueChanged.connect(self._render_frame)
        controls.addWidget(QLabel("Scale"))
        controls.addWidget(self.scale_spin)

        self.flip_check = QCheckBox("Flip")
        self.flip_check.setChecked(self.flipped)
        self.flip_check.toggled.connect(self._toggle_flip)
        controls.addWidget(self.flip_check)

        self.play_btn = QPushButton("Pause")
        self.play_btn.clicked.connect(self._toggle_play)
        controls.addWidget(self.play_btn)

        self.step_back_btn = QPushButton("◀")
        self.step_back_btn.clicked.connect(self._step_back)
        controls.addWidget(self.step_back_btn)

        self.step_fwd_btn = QPushButton("▶")
        self.step_fwd_btn.clicked.connect(self._step_forward)
        controls.addWidget(self.step_fwd_btn)

        self.reload_btn = QPushButton("Reload")
        self.reload_btn.clicked.connect(self._reload_sprites)
        controls.addWidget(self.reload_btn)

        self.custom_btn = QPushButton("Load Custom…")
        self.custom_btn.clicked.connect(self._pick_custom_dir)
        controls.addWidget(self.custom_btn)

        controls.addStretch(1)
        layout.addLayout(controls)

        self.frame_label = QLabel()
        self.frame_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.frame_label.setMinimumSize(200, 200)
        layout.addWidget(self.frame_label, stretch=1)

        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

    def _set_fps(self, fps):
        interval = max(1, int(1000 / fps))
        self.timer.setInterval(interval)
        if self.playing:
            self.timer.start()
        self._update_status()

    def _change_anim(self, anim_name):
        self.current_anim = anim_name
        self.frame_index = 0
        self._render_frame()

    def _toggle_play(self):
        self.playing = not self.playing
        if self.playing:
            self.play_btn.setText("Pause")
            self.timer.start()
        else:
            self.play_btn.setText("Play")
            self.timer.stop()
        self._update_status()

    def _toggle_flip(self, checked):
        self.flipped = checked
        self._render_frame()

    def _step_back(self):
        self.frame_index -= 1
        self._render_frame()

    def _step_forward(self):
        self.frame_index += 1
        self._render_frame()

    def _advance_frame(self):
        self.frame_index += 1
        self._render_frame()

    def _render_frame(self):
        frame = self.renderer.get_frame(self.current_anim, self.frame_index, flipped=self.flipped)
        if frame.isNull():
            self.frame_label.clear()
            return
        scale = self.scale_spin.value()
        w = max(1, int(frame.width() * scale))
        h = max(1, int(frame.height() * scale))
        scaled = frame.scaled(w, h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.FastTransformation)
        self.frame_label.setPixmap(scaled)
        self._update_status()

    def _update_status(self):
        total = self.renderer.frame_count(self.current_anim)
        current = self.frame_index % total if total else 0
        state = "Playing" if self.playing else "Paused"
        custom = f"Custom: {self.custom_dir}" if self.custom_dir else "Custom: (none)"
        self.status_label.setText(
            f"{state} | {self.current_anim} | frame {current + 1}/{max(total, 1)} | {custom}"
        )

    def _reload_sprites(self):
        self.renderer.reload_sprites(self.custom_dir)
        self.frame_index = 0
        self._render_frame()

    def _pick_custom_dir(self):
        start_dir = self.custom_dir or os.path.join(self.assets_dir, "cache")
        picked = QFileDialog.getExistingDirectory(self, "Select Custom Sprite Folder", start_dir)
        if picked:
            self.custom_dir = picked
            self.renderer.reload_sprites(self.custom_dir)
            self.frame_index = 0
            self._render_frame()


def parse_args():
    parser = argparse.ArgumentParser(description="Preview desktop pet animations.")
    parser.add_argument("--assets-dir", default="assets", help="Path to assets directory.")
    parser.add_argument("--custom-dir", default=None, help="Optional custom sprite directory.")
    parser.add_argument("--anim", default="walk", help="Initial animation name.")
    parser.add_argument("--fps", type=int, default=10, help="Frames per second.")
    parser.add_argument("--scale", type=float, default=1.0, help="Display scale.")
    parser.add_argument("--flip", action="store_true", help="Start flipped.")
    return parser.parse_args()


def main():
    args = parse_args()
    app = QApplication(sys.argv)
    window = PreviewWindow(
        assets_dir=args.assets_dir,
        custom_dir=args.custom_dir,
        fps=args.fps,
        scale=args.scale,
        anim=args.anim,
        flipped=args.flip,
    )
    window.resize(640, 520)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
