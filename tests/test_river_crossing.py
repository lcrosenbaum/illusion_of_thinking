import pytest

from illusion_of_thinking.simulators import RiverCrossingSimulator


@pytest.fixture
def make_river_crossing():
    def _make(N=3, k=2):
        return RiverCrossingSimulator(N=N, k=k)

    return _make


def test_init_and_reset(make_river_crossing):
    sim = make_river_crossing()

    # Check initial state
    boat_position, entity_positions = sim.state
    assert boat_position == 0
    assert len(entity_positions) == 6  # 3 actors + 3 agents
    assert all(pos == 0 for pos in entity_positions.values())

    # Modify state then reset
    entity_positions["A_1"] = 1
    entity_positions["a_3"] = 1
    sim.state = (1, entity_positions)
    assert not all(pos == 0 for pos in entity_positions.values())
    sim.reset()
    boat_position, entity_positions = sim.state
    assert boat_position == 0
    assert all(pos == 0 for pos in entity_positions.values())


def test_is_valid_state(make_river_crossing):
    sim = make_river_crossing()

    # Initial state should be valid
    assert sim.is_valid_state()

    # Invalid state: boat position not 0 or 1
    boat_position, entity_positions = sim.state
    sim.state = (2, entity_positions)
    assert not sim.is_valid_state()

    # Reset for next test
    sim.reset()

    # Invalid state: actor with another agent without their own agent
    boat_position, entity_positions = sim.state
    new_positions = entity_positions.copy()
    # Move actor a_1 and agent A_2 to right bank (violates constraint)
    new_positions["a_1"] = 1
    new_positions["A_2"] = 1
    sim.state = (0, new_positions)
    assert not sim.is_valid_state()


def test_valid_move(make_river_crossing):
    sim = make_river_crossing()

    # Valid move: move one agent and its actor
    assert sim.is_valid_move(["a_1", "A_1"])
    assert sim.execute_move(["a_1", "A_1"])

    # Check new state
    boat_position, entity_positions = sim.state
    assert boat_position == 1
    assert entity_positions["A_1"] == 1
    assert entity_positions["a_1"] == 1
    assert all(
        entity_positions[entity] == 0 for entity in entity_positions if entity not in ["a_1", "A_1"]
    )

    # Valid move: move the agent and actor back
    assert sim.is_valid_move(["A_1"])
    assert sim.execute_move(["A_1"])

    # Valid move: move only actor
    assert sim.is_valid_move(["a_2"])
    assert sim.execute_move(["a_2"])


def test_invalid_moves(make_river_crossing):
    sim = make_river_crossing()

    # Invalid move: too many passengers
    assert not sim.is_valid_move(["A_1", "a_1", "A_2"])

    # Invalid move: invalid entity
    assert not sim.is_valid_move(["invalid_entity"])

    # Invalid move: moving agent with too high id
    assert not sim.is_valid_move(["A_4"])

    # Empty boat is not allowed
    assert not sim.is_valid_move([])

    # Invalid move: duplicate entities
    assert not sim.is_valid_move(["A_1", "A_1"])

    # Move boat to right bank
    sim.execute_move(["a_1"])

    # Invalid move: passengers not at boat location
    assert not sim.is_valid_move(["A_1"])


def test_constraints(make_river_crossing):
    sim = make_river_crossing()

    # Valid move: move one agent and its actor
    assert sim.is_valid_move(["a_1", "A_1"])
    assert sim.execute_move(["a_1", "A_1"])

    # Check new state
    boat_position, entity_positions = sim.state
    assert boat_position == 1
    assert entity_positions["A_1"] == 1
    assert entity_positions["a_1"] == 1

    # Invalid move: actor a_2 is not with its agent A_2
    assert not sim.is_valid_move(["a_2", "A_2"])

    # Valid move: Move agent back, because A_2 is still present on left side
    assert sim.execute_move(["A_1"])

    # Move itself is valid, but executing it results in invalid state
    # causing execute to fail
    assert sim.is_valid_move(["a_2", "A_2"])
    assert not sim.execute_move(["a_2", "A_2"])


def test_goal_reached():
    sim = RiverCrossingSimulator(N=2, k=2)
    assert not sim.is_goal_reached()

    # Create a solution for 2 actor-agent pairs
    # Move move all actors to right bank
    assert sim.execute_move(["a_1", "a_2"])
    assert not sim.is_goal_reached()

    # Move a_1 back to left bank
    assert sim.execute_move(["a_1"])
    assert not sim.is_goal_reached()

    # Move both agents to right bank
    assert sim.execute_move(["A_1", "A_2"])
    assert not sim.is_goal_reached()

    # Move A_1 back to left bank
    assert sim.execute_move(["A_1"])
    assert not sim.is_goal_reached()

    # Move A_1 and a_1 to right bank
    assert sim.execute_move(["A_1", "a_1"])
    assert sim.is_goal_reached()


def test_reset_with_valid_and_invalid_state(make_river_crossing):
    sim = make_river_crossing(N=2, k=2)
    # Valid state: all on right bank, boat on right
    valid_state = (1, {"a_1": 1, "A_1": 1, "a_2": 1, "A_2": 1})
    sim.reset(valid_state)
    assert sim.state == valid_state
    assert sim.is_valid_state()

    # Invalid state: actor a_1 with agent A_2, but not with own agent A_1
    invalid_state = (0, {"a_1": 1, "A_1": 0, "a_2": 0, "A_2": 1})
    with pytest.raises(ValueError):
        sim.reset(invalid_state)
    # State should remain unchanged (should still be valid_state)
    assert sim.state == valid_state

    # Invalid state: actor a_1 with agent A_2, but not with own agent A_1
    invalid_state = (0, {"a_1": 0, "A_1": 0, "a_2": 0, "A_2": 0, "a_3": 0, "A_3": 0})
    with pytest.raises(ValueError):
        sim.reset(invalid_state)
    # State should remain unchanged (should still be valid_state)
    assert sim.state == valid_state
