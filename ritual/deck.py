"""Tarot deck: load card definitions from YAML, shuffle, draw."""

from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass(frozen=True)
class Card:
    name: str
    upright_meaning: str
    reversed_meaning: str
    image: str | None = None


@dataclass(frozen=True)
class DrawnCard:
    card: Card
    reversed: bool

    @property
    def meaning(self) -> str:
        return self.card.reversed_meaning if self.reversed else self.card.upright_meaning

    @property
    def orientation(self) -> str:
        return "reversed" if self.reversed else "upright"


class Deck:
    def __init__(self, cards: list[Card]) -> None:
        self.cards = cards

    @classmethod
    def load(cls, deck_dir: Path) -> "Deck":
        with open(Path(deck_dir) / "cards.yaml") as f:
            data = yaml.safe_load(f) or []
        cards = [Card(**entry) for entry in data]
        return cls(cards)

    def draw(self, n: int = 3) -> list[DrawnCard]:
        if n > len(self.cards):
            raise ValueError(f"requested {n} cards, deck has {len(self.cards)}")
        picks = random.sample(self.cards, n)
        return [DrawnCard(card=c, reversed=random.random() < 0.5) for c in picks]
