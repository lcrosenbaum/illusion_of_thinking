"""
Unit tests for simulator tools.

These tests verify that the simulator tools work correctly for both simulator types
and handle error cases appropriately.
"""

from typing import Any, Dict, List

import pytest

from illusion_of_thinking.simulator_tools import (
    CreateSimulatorTool,
    ExecuteMovesTool,
    GetStateTool,
    ResetSimulatorTool,
    get_current_simulator,
    set_current_simulator,
)
from illusion_of_thinking.simulators import RiverCrossingSimulator, TowerOfHanoiSimulator


class TestCreateSimulatorTool:
    def setup_method(self):
        # Reset the global simulator before each test
        set_current_simulator(None)

    def test_create_tower_of_hanoi(self):
        tool = CreateSimulatorTool()
        result = tool.forward(simulator_type="TowerOfHanoi", N=3)

        assert "error" not in result
        assert result["simulator_type"] == "TowerOfHanoi"
        assert result["simulator_params"]["N"] == 3
        assert isinstance(get_current_simulator(), TowerOfHanoiSimulator)

    def test_create_river_crossing(self):
        tool = CreateSimulatorTool()
        result = tool.forward(simulator_type="RiverCrossing", N=2, k=2)

        assert "error" not in result
        assert result["simulator_type"] == "RiverCrossing"
        assert result["simulator_params"]["N"] == 2
        assert result["simulator_params"]["k"] == 2
        assert isinstance(get_current_simulator(), RiverCrossingSimulator)

    def test_create_invalid_simulator_type(self):
        tool = CreateSimulatorTool()
        result = tool.forward(simulator_type="InvalidType", N=3)

        assert "error" in result
        assert get_current_simulator() is None

    def test_create_invalid_N(self):
        tool = CreateSimulatorTool()
        result = tool.forward(simulator_type="TowerOfHanoi", N=0)

        assert "error" in result
        assert get_current_simulator() is None

    def test_create_invalid_k(self):
        tool = CreateSimulatorTool()
        result = tool.forward(simulator_type="RiverCrossing", N=2, k=0)

        assert "error" in result
        assert get_current_simulator() is None


class TestResetSimulatorTool:
    def setup_method(self):
        # Reset the global simulator before each test
        set_current_simulator(None)

        # Create a simulator for testing
        tool = CreateSimulatorTool()
        tool.forward(simulator_type="TowerOfHanoi", N=3)

    def test_reset_to_default(self):
        current_simulator = get_current_simulator()

        # Execute a move to change the state
        current_simulator.execute_move([1, 0, 2])
        assert current_simulator.state != ([3, 2, 1], [], [])

        # Reset to default state
        tool = ResetSimulatorTool()
        result = tool.forward()

        assert "error" not in result
        assert result["reset_successful"] is True
        assert current_simulator.state == ([3, 2, 1], [], [])

    def test_reset_to_custom_state(self):
        current_simulator = get_current_simulator()

        # Custom state: move the first disk to the third peg
        custom_state = ([3, 2], [], [1])

        tool = ResetSimulatorTool()
        result = tool.forward(state=custom_state)

        assert "error" not in result
        assert result["reset_successful"] is True
        assert current_simulator.state == ([3, 2], [], [1])

    def test_reset_invalid_state(self):
        # Invalid state: missing a disk
        invalid_state = ([3, 2], [], [])

        tool = ResetSimulatorTool()
        result = tool.forward(state=invalid_state)

        assert "error" in result
        assert result["reset_successful"] is False

    def test_reset_no_simulator(self):
        # No simulator initialized
        set_current_simulator(None)

        tool = ResetSimulatorTool()
        result = tool.forward()

        assert "error" in result


class TestGetStateTool:
    def setup_method(self):
        # Reset the global simulator before each test
        global current_simulator
        current_simulator = None

    def test_get_state_tower_of_hanoi(self):
        # Create a Tower of Hanoi simulator
        create_tool = CreateSimulatorTool()
        create_tool.forward(simulator_type="TowerOfHanoi", N=3)

        # Get the state
        tool = GetStateTool()
        result = tool.forward()

        assert "error" not in result
        assert result["simulator_type"] == "TowerOfHanoi"
        assert result["simulator_params"]["N"] == 3
        assert result["state"] == ([3, 2, 1], [], [])
        assert result["goal_reached"] is False

    def test_get_state_river_crossing(self):
        # Create a River Crossing simulator
        create_tool = CreateSimulatorTool()
        create_tool.forward(simulator_type="RiverCrossing", N=2, k=2)

        # Get the state
        tool = GetStateTool()
        result = tool.forward()

        assert "error" not in result
        assert result["simulator_type"] == "RiverCrossing"
        assert result["simulator_params"]["N"] == 2
        assert result["simulator_params"]["k"] == 2
        assert result["goal_reached"] is False

    def test_get_state_no_simulator(self):
        set_current_simulator(None)

        tool = GetStateTool()
        result = tool.forward()

        assert "error" in result


class TestExecuteMovesTool:
    def setup_method(self):
        # Reset the global simulator before each test
        global current_simulator
        current_simulator = None

    def test_execute_moves_tower_of_hanoi(self):
        # Create a Tower of Hanoi simulator
        create_tool = CreateSimulatorTool()
        create_tool.forward(simulator_type="TowerOfHanoi", N=3)

        # Define a sequence of moves
        moves = [
            [1, 0, 2],  # Move disk 1 from peg 0 to peg 2
            [2, 0, 1],  # Move disk 2 from peg 0 to peg 1
            [1, 2, 1],  # Move disk 1 from peg 2 to peg 1
        ]

        # Execute the moves
        tool = ExecuteMovesTool()
        result = tool.forward(moves=moves)

        assert "error" not in result
        assert result["all_moves_successful"] is True
        assert len(result["move_results"]) == 3
        assert result["final_state"] == ([3], [2, 1], [])
        assert result["goal_reached"] is False

    def test_execute_invalid_move_tower_of_hanoi(self):
        # Create a Tower of Hanoi simulator
        create_tool = CreateSimulatorTool()
        create_tool.forward(simulator_type="TowerOfHanoi", N=3)

        # Define a sequence of moves with an invalid move
        moves = [
            [1, 0, 2],  # Valid: Move disk 1 from peg 0 to peg 2
            [3, 0, 1],  # Invalid: Move disk 3 from peg 0 to peg 1 (disk 2 is on top)
        ]

        # Execute the moves
        tool = ExecuteMovesTool()
        result = tool.forward(moves=moves)

        assert "error" not in result
        assert result["all_moves_successful"] is False
        assert len(result["move_results"]) == 2
        assert result["move_results"][0]["successful"] is True
        assert result["move_results"][1]["successful"] is False
        assert result["final_state"] == ([3, 2], [], [1])

    def test_execute_moves_river_crossing(self):
        # Create a River Crossing simulator
        create_tool = CreateSimulatorTool()
        create_tool.forward(simulator_type="RiverCrossing", N=2, k=2)

        # Define a sequence of moves
        moves = [
            ["A_1", "a_1"],  # Agent 1 and Actor 1 cross
            ["A_1"],  # Agent 1 returns
            ["A_1", "A_2"],  # Agent 1 and Agent 2 cross
            ["a_1"],  # Actor 1 returns
            ["a_1", "a_2"],  # Actor 1 and Actor 2 cross
        ]

        # Execute the moves
        tool = ExecuteMovesTool()
        result = tool.forward(moves=moves)

        assert "error" not in result
        assert result["all_moves_successful"] is True
        assert len(result["move_results"]) == 5
        assert result["goal_reached"] is True

    def test_execute_invalid_move_river_crossing(self):
        # Create a River Crossing simulator
        create_tool = CreateSimulatorTool()
        create_tool.forward(simulator_type="RiverCrossing", N=2, k=2)

        # Define a sequence of moves with an invalid move
        moves = [
            ["A_1", "a_1"],  # Valid: Agent 1 and Actor 1 cross
            [
                "a_2"
            ],  # Invalid: Actor 2 cannot cross alone (would be with Agent 1 without its own agent)
        ]

        # Execute the moves
        tool = ExecuteMovesTool()
        result = tool.forward(moves=moves)

        assert "error" not in result
        assert result["all_moves_successful"] is False
        assert len(result["move_results"]) == 2
        assert result["move_results"][0]["successful"] is True
        assert result["move_results"][1]["successful"] is False
        assert result["goal_reached"] is False

    def test_execute_moves_no_simulator(self):
        # No simulator initialized
        set_current_simulator(None)

        tool = ExecuteMovesTool()
        result = tool.forward(moves=[[1, 0, 2]])

        assert "error" in result
