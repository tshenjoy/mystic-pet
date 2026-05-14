"""Ceremony window: question -> shuffle -> draw -> reading -> close."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from ritual.deck import Deck
from ritual.reader import Reader


class CeremonyWindow(QDialog):
    def __init__(self, deck: Deck, reader: Reader, spread_size: int = 3, parent=None) -> None:
        super().__init__(parent)
        self.deck = deck
        self.reader = reader
        self.spread_size = spread_size

        self.setWindowTitle("ritual")
        self.setMinimumSize(520, 480)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        layout = QVBoxLayout(self)

        self.prompt_label = QLabel("what brings you, traveler?")
        self.prompt_label.setStyleSheet("font-size: 16px; font-style: italic;")
        layout.addWidget(self.prompt_label)

        self.question_input = QLineEdit()
        self.question_input.setPlaceholderText("(or leave blank for an open reading)")
        layout.addWidget(self.question_input)

        self.cards_row = QHBoxLayout()
        layout.addLayout(self.cards_row)

        self.reading_text = QTextEdit()
        self.reading_text.setReadOnly(True)
        self.reading_text.setPlaceholderText("the reading will appear here...")
        layout.addWidget(self.reading_text)

        button_row = QHBoxLayout()
        self.draw_button = QPushButton("draw the cards")
        self.draw_button.clicked.connect(self._on_draw)
        self.close_button = QPushButton("close the curtain")
        self.close_button.clicked.connect(self.accept)
        button_row.addWidget(self.draw_button)
        button_row.addStretch(1)
        button_row.addWidget(self.close_button)
        layout.addLayout(button_row)

    def _on_draw(self) -> None:
        self.draw_button.setEnabled(False)
        self.draw_button.setText("the cards are speaking...")

        for i in reversed(range(self.cards_row.count())):
            item = self.cards_row.takeAt(i)
            if item.widget():
                item.widget().deleteLater()

        drawn = self.deck.draw(self.spread_size)
        for dc in drawn:
            self.cards_row.addWidget(self._render_card_label(dc))

        question = self.question_input.text()
        reading = self.reader.read(question, drawn)
        self.reading_text.setPlainText(reading)

        self.draw_button.setText("draw again")
        self.draw_button.setEnabled(True)

    @staticmethod
    def _render_card_label(dc) -> QLabel:
        text = f"{dc.card.name}\n({dc.orientation})"
        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(
            "border: 1px solid #444; padding: 12px; background: #f8f4ec; min-width: 100px;"
        )
        return lbl
