"""Mystic Pet — entry point."""

from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QColor, QIcon, QPainter, QPixmap
from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from config import settings as settings_module
from llm.client import LLMClient
from pet.overlay import PetOverlay
from ritual.ceremony_window import CeremonyWindow
from ritual.deck import Deck
from ritual.reader import Reader
from whisper.library import WhisperLibrary
from whisper.scheduler import WhisperScheduler

_ASSETS = Path(__file__).parent / "assets"
_DEFAULT_DECK = Path(__file__).parent / "ritual" / "decks" / "default"


def _make_tray_icon() -> QIcon:
    px = QPixmap(32, 32)
    px.fill(Qt.GlobalColor.transparent)
    p = QPainter(px)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QColor(120, 90, 180))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(4, 8, 24, 20)
    p.setBrush(QColor(40, 20, 70))
    p.drawRect(6, 4, 20, 6)
    p.end()
    return QIcon(px)


def main() -> int:
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    cfg = settings_module.load()

    overlay = PetOverlay(
        assets_dir=_ASSETS,
        position=(cfg["pet"]["position"]["x"], cfg["pet"]["position"]["y"]),
    )
    overlay.show()

    library = WhisperLibrary(categories=cfg["whisper"]["categories"])
    scheduler = WhisperScheduler(
        interval_minutes=cfg["whisper"]["interval_minutes"],
        jitter_pct=cfg["whisper"]["jitter_pct"],
    )

    def _on_whisper_due():
        line = library.random()
        # Phase 1: print to stdout. Phase 2: render speech bubble next to pet.
        print(f"[whisper] {line}")

    scheduler.whisper_due.connect(_on_whisper_due)
    if cfg["whisper"]["enabled"]:
        scheduler.start()

    deck = Deck.load(_DEFAULT_DECK)
    llm = LLMClient(
        model=cfg["llm"]["model"],
        max_tokens=cfg["llm"]["max_tokens"],
        timeout_seconds=cfg["llm"]["timeout_seconds"],
    )
    reader = Reader(llm)

    def _open_ceremony():
        window = CeremonyWindow(deck, reader, spread_size=cfg["ritual"]["spread_size"], parent=overlay)
        window.exec()

    overlay.pet_clicked.connect(_open_ceremony)

    tray = QSystemTrayIcon(_make_tray_icon(), app)
    menu = QMenu()

    toggle = QAction("Hide pet", menu)
    def _toggle():
        new_hidden = not overlay.is_user_hidden
        overlay.set_user_hidden(new_hidden)
        toggle.setText("Show pet" if new_hidden else "Hide pet")
    toggle.triggered.connect(_toggle)
    menu.addAction(toggle)

    ritual_action = QAction("Open ritual...", menu)
    ritual_action.triggered.connect(_open_ceremony)
    menu.addAction(ritual_action)

    menu.addSeparator()
    quit_action = QAction("Quit", menu)
    quit_action.triggered.connect(app.quit)
    menu.addAction(quit_action)

    tray.setContextMenu(menu)
    tray.setToolTip("Mystic Pet")
    tray.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
