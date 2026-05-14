from pathlib import Path

import pytest

from ritual.deck import Deck, DrawnCard

DECK_PATH = Path(__file__).parent.parent / "ritual" / "decks" / "default"


def test_deck_loads():
    deck = Deck.load(DECK_PATH)
    assert len(deck.cards) > 0


def test_deck_draws_n():
    deck = Deck.load(DECK_PATH)
    drawn = deck.draw(3)
    assert len(drawn) == 3
    for d in drawn:
        assert isinstance(d, DrawnCard)
        assert d.meaning


def test_draw_too_many_raises():
    deck = Deck.load(DECK_PATH)
    with pytest.raises(ValueError):
        deck.draw(len(deck.cards) + 1)
