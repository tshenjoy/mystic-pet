"""Pet state machine: idle / whispering / ritual."""

from enum import Enum


class State(Enum):
    IDLE = "idle"
    WHISPERING = "whispering"
    RITUAL = "ritual"


class StateMachine:
    def __init__(self) -> None:
        self.state = State.IDLE

    def to_idle(self) -> None:
        self.state = State.IDLE

    def to_whispering(self) -> None:
        self.state = State.WHISPERING

    def to_ritual(self) -> None:
        self.state = State.RITUAL
