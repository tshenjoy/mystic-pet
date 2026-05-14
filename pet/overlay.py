"""Transparent always-on-top overlay window that hosts the pet."""

from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from pet.pet_widget import PetWidget
from pet.sprite_renderer import SpriteRenderer
from pet.state_machine import StateMachine


class PetOverlay(QWidget):
    pet_clicked = pyqtSignal()

    REPAINT_MS = 33  # ~30 fps

    def __init__(self, assets_dir: Path, position: tuple[int, int] = (100, 100)) -> None:
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

        self.renderer = SpriteRenderer(Path(assets_dir))
        self.state_machine = StateMachine()
        self._user_hidden = False

        self.pet = PetWidget(self.renderer, self)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.pet)

        self.pet.clicked.connect(self.pet_clicked.emit)

        self.move(*position)
        self.renderer.start()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.pet.update)
        self.timer.start(self.REPAINT_MS)

    def set_user_hidden(self, hidden: bool) -> None:
        self._user_hidden = hidden
        self.setVisible(not hidden)

    @property
    def is_user_hidden(self) -> bool:
        return self._user_hidden
