import pytest

from illusion_of_thinking.simulators import TowerOfHanoiSimulator


@pytest.fixture
def hanoi():
    return TowerOfHanoiSimulator(3)


def test_initial_state(hanoi):
    # Initial state: all disks on first peg (largest disk 3 at bottom, smallest disk 1 at top)
    assert hanoi.state == ([3, 2, 1], [], [])
    assert hanoi.is_valid_state()
    assert not hanoi.is_goal_reached()


def test_valid_move(hanoi):
    # Move disk 1 (smallest) from peg 0 to peg 2
    assert hanoi.is_valid_move((1, 0, 2))
    assert hanoi.execute_move((1, 0, 2))
    assert hanoi.state == ([3, 2], [], [1])
    assert hanoi.is_valid_state()
    assert not hanoi.is_goal_reached()


def test_invalid_move_wrong_disk(hanoi):
    # Try to move disk 2 from peg 0 to peg 2 (not the top disk)
    assert not hanoi.is_valid_move((2, 0, 2))
    assert not hanoi.execute_move((2, 0, 2))
    assert hanoi.state == ([3, 2, 1], [], [])


def test_invalid_move_larger_onto_smaller(hanoi):
    # Move disk 1 (smallest) to peg 2, then try to move disk 2 (larger) onto disk 1
    hanoi.execute_move((1, 0, 2))
    assert not hanoi.is_valid_move((2, 0, 2))
    assert not hanoi.execute_move((2, 0, 2))


def test_goal_state():
    hanoi = TowerOfHanoiSimulator(2)
    # Move all disks to peg 2 in the optimal sequence
    assert hanoi.execute_move((1, 0, 1))  # Move disk 1 from peg 0 to peg 1
    assert hanoi.execute_move((2, 0, 2))  # Move disk 2 from peg 0 to peg 2
    assert hanoi.execute_move((1, 1, 2))  # Move disk 1 from peg 1 to peg 2
    assert hanoi.is_goal_reached()


def test_reset(hanoi):
    hanoi.execute_move((1, 0, 2))
    hanoi.reset()
    assert hanoi.state == ([3, 2, 1], [], [])
    assert hanoi.is_valid_state()


def test_reset_with_valid_state(hanoi):
    # Valid state: disk 1 on peg 2, disks 2 and 3 on peg 0
    valid_state = ([3, 2], [], [1])
    hanoi.reset(valid_state)
    assert hanoi.state == valid_state
    assert hanoi.is_valid_state()


def test_reset_with_invalid_state(hanoi):
    # Invalid state: disk 2 on top of disk 1 (wrong order)
    invalid_state = ([1, 2, 3], [], [])
    with pytest.raises(ValueError):
        hanoi.reset(invalid_state)
    # State should remain unchanged (should still be initial state)
    assert hanoi.state == ([3, 2, 1], [], [])

    invalid_state = ([4, 3, 2, 1], [], [])
    with pytest.raises(ValueError):
        hanoi.reset(invalid_state)
