"""Cat behavior state machine."""

from enum import Enum, auto
import random
import time


class State(Enum):
    IDLE = auto()
    WALK = auto()
    STALK = auto()
    CHASE = auto()
    TRASH_CAN = auto()


class Direction(Enum):
    LEFT = -1
    RIGHT = 1


class StateMachine:
    """Manages cat behavior transitions.

    The cat cycles through states based on timers and cursor proximity.
    IDLE is the hub state — all other states return to IDLE when done.
    """

    # How long each state lasts (seconds)
    STATE_DURATION = {
        State.IDLE: (2, 4),
        State.WALK: (4, 8),
        State.STALK: (3, 5),
        State.CHASE: (3, 6),
        State.TRASH_CAN: (4, 7),
    }

    # Chance of transitioning from IDLE to each state (weights)
    IDLE_TRANSITIONS = {
        State.WALK: 50,
        State.STALK: 25,
        State.TRASH_CAN: 15,
    }

    CHASE_TRIGGER_DISTANCE = 150  # pixels — cursor must be this close to trigger chase

    # Click cycles through these states in order
    CLICK_CYCLE = [State.IDLE, State.WALK, State.STALK, State.TRASH_CAN]

    def __init__(self):
        self.state = State.IDLE
        self.direction = Direction.RIGHT
        self.state_start_time = time.time()
        self.state_duration = self._random_duration(State.IDLE)

    def _random_duration(self, state):
        low, high = self.STATE_DURATION[state]
        return random.uniform(low, high)

    def _pick_next_from_idle(self):
        states = list(self.IDLE_TRANSITIONS.keys())
        weights = list(self.IDLE_TRANSITIONS.values())
        return random.choices(states, weights=weights, k=1)[0]

    def update(self, cursor_distance=None):
        """Called each tick. Returns current state.

        Args:
            cursor_distance: pixel distance from cursor to cat. None if unknown.
        """
        elapsed = time.time() - self.state_start_time

        # Chase interrupts any state if cursor is close enough
        if (cursor_distance is not None
                and cursor_distance < self.CHASE_TRIGGER_DISTANCE
                and self.state != State.CHASE):
            self._enter_state(State.CHASE)
            return self.state

        # Check if current state duration expired
        if elapsed >= self.state_duration:
            if self.state == State.IDLE:
                next_state = self._pick_next_from_idle()
                self._enter_state(next_state)
            else:
                self._enter_state(State.IDLE)

        return self.state

    def on_click(self):
        """User clicked the cat — cycle to next behavior."""
        try:
            idx = self.CLICK_CYCLE.index(self.state)
            next_state = self.CLICK_CYCLE[(idx + 1) % len(self.CLICK_CYCLE)]
        except ValueError:
            next_state = State.IDLE
        self._enter_state(next_state)
        return self.state

    def _enter_state(self, new_state):
        self.state = new_state
        self.state_start_time = time.time()
        self.state_duration = self._random_duration(new_state)

        if new_state == State.WALK:
            if random.random() < 0.5:
                self.direction = Direction.LEFT if self.direction == Direction.RIGHT else Direction.RIGHT
