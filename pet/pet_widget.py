"""The cat pet — handles position, animation, and movement logic."""

import math
from PyQt6.QtCore import QPoint
from pet.state_machine import State, Direction


class PetCat:
    """Manages cat position, animation frame, and movement.

    This is pure logic — no Qt widgets. The overlay window reads
    position/frame from here and draws accordingly.
    """

    WALK_SPEED = 2        # pixels per tick
    CHASE_SPEED = 4
    STALK_SPEED = 1

    def __init__(self, sprite_renderer):
        self.renderer = sprite_renderer
        self.x = 100
        self.y = 0
        self.frame_index = 0
        self.ticks_per_frame = 6   # slow down animation (tick = ~33ms at 30fps)
        self.tick_counter = 0

    def animation_name(self, state):
        """Map state enum to sprite animation name."""
        return {
            State.IDLE: "idle",
            State.WALK: "walk",
            State.STALK: "stalk",
            State.CHASE: "chase",
            State.TRASH_CAN: "trash_can",
        }.get(state, "idle")

    def update(self, state, direction, window_rect, cursor_pos=None):
        """Move cat and advance animation frame.

        Args:
            state: current State enum
            direction: Direction enum (LEFT/RIGHT)
            window_rect: WindowRect of active window
            cursor_pos: (x, y) tuple of mouse cursor, or None
        """
        anim = self.animation_name(state)

        # Advance animation frame
        self.tick_counter += 1
        if self.tick_counter >= self.ticks_per_frame:
            self.tick_counter = 0
            self.frame_index += 1

        # Cat sits on top edge of window
        self.y = window_rect.top - self.renderer.sprite_h

        # Movement based on state
        if state == State.WALK:
            self._move_walk(direction, window_rect)
        elif state == State.STALK:
            self._move_stalk(direction, window_rect)
        elif state == State.CHASE and cursor_pos:
            self._move_chase(cursor_pos, window_rect)
        elif state == State.IDLE:
            pass  # stay put
        elif state == State.TRASH_CAN:
            pass  # stay put, animation plays

        return self.get_current_frame(anim)

    def _move_walk(self, direction, window_rect):
        self.x += self.WALK_SPEED * direction.value
        self._clamp_to_window(window_rect)

    def _move_stalk(self, direction, window_rect):
        self.x += self.STALK_SPEED * direction.value
        self._clamp_to_window(window_rect)

    def _move_chase(self, cursor_pos, window_rect):
        cx, cy = cursor_pos
        if cx > self.x + self.renderer.sprite_w // 2:
            self.x += self.CHASE_SPEED
        elif cx < self.x + self.renderer.sprite_w // 2:
            self.x -= self.CHASE_SPEED
        self._clamp_to_window(window_rect)

    def _clamp_to_window(self, window_rect):
        """Keep cat within window's top edge bounds."""
        self.x = max(window_rect.left, min(self.x, window_rect.right - self.renderer.sprite_w))

    def get_current_frame(self, anim_name):
        return self.renderer.get_frame(anim_name, self.frame_index)

    def cursor_distance(self, cursor_pos):
        """Distance from cat center to cursor."""
        if cursor_pos is None:
            return None
        cx, cy = cursor_pos
        cat_cx = self.x + self.renderer.sprite_w // 2
        cat_cy = self.y + self.renderer.sprite_h // 2
        return math.hypot(cx - cat_cx, cy - cat_cy)

    @property
    def position(self):
        return QPoint(self.x, self.y)
