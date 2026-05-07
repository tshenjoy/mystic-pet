"""The cat pet — handles position, animation, and movement logic."""

import math
from PyQt6.QtCore import QPoint
from pet.state_machine import State, Direction


class PetCat:
    """Manages cat position, animation frame, and movement.

    display_scale controls how big the cat appears on screen.
    All position math uses the scaled (display) size.
    """

    WALK_SPEED = 2
    CHASE_SPEED = 4
    STALK_SPEED = 1

    # Window tracker may report bounds that include window shadow/title bar.
    # Adjust this to move the cat vertically relative to the reported window top.
    # Positive = lower (closer to window content), Negative = higher.
    WINDOW_Y_OFFSET = 0

    def __init__(self, sprite_renderer, display_scale=0.25):
        self.renderer = sprite_renderer
        self.display_scale = display_scale
        self.x = 100
        self.y = 0
        self.frame_index = 0
        self.ticks_per_frame = 6
        self.tick_counter = 0
        self._needs_direction_flip = False

    @property
    def display_w(self):
        return int(self.renderer.sprite_w * self.display_scale)

    @property
    def display_h(self):
        return int(self.renderer.sprite_h * self.display_scale)

    def animation_name(self, state):
        return {
            State.IDLE: "idle",
            State.WALK: "walk",
            State.STALK: "stalk",
            State.CHASE: "chase",
            State.TRASH_CAN: "trash_can",
        }.get(state, "idle")

    def update(self, state, direction, window_rect, cursor_pos=None):
        anim = self.animation_name(state)

        # Only animate when moving — freeze on frame 0 during IDLE
        if state == State.IDLE:
            # Cycle through idle frames instead of freezing
            self.tick_counter += 1
            if self.tick_counter >= self.ticks_per_frame:
                self.tick_counter = 0
                self.frame_index += 1
        else:
            self.tick_counter += 1
            if self.tick_counter >= self.ticks_per_frame:
                self.tick_counter = 0
                self.frame_index += 1

        # Cat feet sit on the visible window top edge
        self.y = window_rect.top - self.display_h + self.WINDOW_Y_OFFSET

        if state == State.WALK:
            self._move_walk(direction, window_rect)
        elif state == State.STALK:
            self._move_stalk(direction, window_rect)
        elif state == State.CHASE and cursor_pos:
            self._move_chase(cursor_pos, window_rect)

        return self.get_current_frame(anim)

    def _move_walk(self, direction, window_rect):
        self.x += self.WALK_SPEED * direction.value
        self._bounce_at_edges(window_rect)

    def _move_stalk(self, direction, window_rect):
        self.x += self.STALK_SPEED * direction.value
        self._bounce_at_edges(window_rect)

    def _move_chase(self, cursor_pos, window_rect):
        cx, cy = cursor_pos
        cat_center = self.x + self.display_w // 2
        if cx > cat_center:
            self.x += self.CHASE_SPEED
        elif cx < cat_center:
            self.x -= self.CHASE_SPEED
        self._clamp_to_window(window_rect)

    def _bounce_at_edges(self, window_rect):
        left_bound = window_rect.left
        right_bound = window_rect.right - self.display_w
        if self.x <= left_bound:
            self.x = left_bound
            self._needs_direction_flip = True
        elif self.x >= right_bound:
            self.x = right_bound
            self._needs_direction_flip = True
        else:
            self._needs_direction_flip = False

    def _clamp_to_window(self, window_rect):
        self.x = max(window_rect.left, min(self.x, window_rect.right - self.display_w))

    def get_current_frame(self, anim_name, flipped=False):
        return self.renderer.get_frame(anim_name, self.frame_index, flipped=flipped)

    def cursor_distance(self, cursor_pos):
        if cursor_pos is None:
            return None
        cx, cy = cursor_pos
        cat_cx = self.x + self.display_w // 2
        cat_cy = self.y + self.display_h // 2
        return math.hypot(cx - cat_cx, cy - cat_cy)

    @property
    def needs_direction_flip(self):
        return self._needs_direction_flip

    def contains_point(self, x, y):
        return (self.x <= x <= self.x + self.display_w
                and self.y <= y <= self.y + self.display_h)

    @property
    def position(self):
        return QPoint(self.x, self.y)
