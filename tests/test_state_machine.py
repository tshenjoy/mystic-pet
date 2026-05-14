"""Tests for the cat state machine."""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pet.state_machine import StateMachine, State, Direction


def test_initial_state():
    sm = StateMachine()
    assert sm.state == State.IDLE
    assert sm.direction in (Direction.LEFT, Direction.RIGHT)


def test_stays_idle_briefly():
    sm = StateMachine()
    state = sm.update(cursor_distance=None)
    assert state == State.IDLE


def test_transitions_after_idle_expires():
    sm = StateMachine()
    sm.state_duration = 0
    sm.state_start_time = time.time() - 1
    state = sm.update(cursor_distance=None)
    assert state == State.SITTING  # IDLE -> SITTING
    sm.state_duration = 0
    sm.state_start_time = time.time() - 1
    state = sm.update(cursor_distance=None)
    assert state == State.STANDING  # SITTING -> STANDING
    sm.state_duration = 0
    sm.state_start_time = time.time() - 1
    state = sm.update(cursor_distance=None)
    assert state in (State.WALK, State.STALK, State.TRASH_CAN)


def test_returns_to_idle_after_action():
    sm = StateMachine()
    sm._enter_state(State.WALK)
    sm.state_duration = 0
    sm.state_start_time = time.time() - 1
    state = sm.update(cursor_distance=None)
    assert state == State.IDLE


def test_chase_triggered_by_cursor_proximity():
    sm = StateMachine()
    state = sm.update(cursor_distance=50)  # close enough
    assert state == State.CHASE


def test_chase_not_triggered_when_far():
    sm = StateMachine()
    state = sm.update(cursor_distance=500)
    assert state != State.CHASE


def test_chase_interrupts_walk():
    sm = StateMachine()
    sm._enter_state(State.WALK)
    state = sm.update(cursor_distance=30)
    assert state == State.CHASE


def test_click_cycles_state():
    sm = StateMachine()
    assert sm.state == State.IDLE
    sm.on_click()
    assert sm.state == State.SITTING  # IDLE not in cycle, falls to SITTING
    sm.on_click()
    assert sm.state == State.WALK
    sm.on_click()
    assert sm.state == State.STALK
    sm.on_click()
    assert sm.state == State.TRASH_CAN
    sm.on_click()
    assert sm.state == State.SITTING  # wraps around


def test_click_from_chase_goes_to_sitting():
    sm = StateMachine()
    sm._enter_state(State.CHASE)
    sm.on_click()
    assert sm.state == State.SITTING


def test_direction_changes():
    sm = StateMachine()
    initial = sm.direction
    flipped = False
    for _ in range(50):
        # STANDING -> expired -> picks WALK/STALK/TRASH_CAN (WALK may flip direction)
        sm._enter_state(State.STANDING)
        sm.state_duration = 0
        sm.state_start_time = time.time() - 1
        sm.update(cursor_distance=None)
        if sm.direction != initial:
            flipped = True
            break
    assert flipped


if __name__ == "__main__":
    tests = [v for k, v in list(globals().items()) if k.startswith("test_")]
    passed = 0
    for test in tests:
        try:
            test()
            print(f"  PASS  {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  FAIL  {test.__name__}: {e}")
        except Exception as e:
            print(f"  ERROR {test.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} passed")
