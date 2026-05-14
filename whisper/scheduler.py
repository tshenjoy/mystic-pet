"""Whisper scheduler: jittered timer that emits whisper events."""

from __future__ import annotations

import random

from PyQt6.QtCore import QObject, QTimer, pyqtSignal


class WhisperScheduler(QObject):
    whisper_due = pyqtSignal()

    def __init__(self, interval_minutes: float, jitter_pct: float = 20, parent=None) -> None:
        super().__init__(parent)
        self.interval_minutes = interval_minutes
        self.jitter_pct = jitter_pct
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self._fire)

    def start(self) -> None:
        self._schedule_next()

    def stop(self) -> None:
        self.timer.stop()

    def set_interval(self, interval_minutes: float) -> None:
        self.interval_minutes = interval_minutes
        if self.timer.isActive():
            self.timer.stop()
            self._schedule_next()

    def _schedule_next(self) -> None:
        base_ms = self.interval_minutes * 60_000
        jitter = base_ms * (self.jitter_pct / 100)
        delay = max(1000, int(base_ms + random.uniform(-jitter, jitter)))
        self.timer.start(delay)

    def _fire(self) -> None:
        self.whisper_due.emit()
        self._schedule_next()
