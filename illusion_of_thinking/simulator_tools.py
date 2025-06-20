"""
Tool implementations for interacting with simulation environments.

These tools provide a structured interface to the simulation functionality,
following the Tool pattern. This simplified version assumes only one active
simulator at a time.
"""

from typing import Any, Dict, List, Optional, Union

from smolagents import Tool

from .constants import SimulationType
from .simulators import RiverCrossingSimulator, Simulator, TowerOfHanoiSimulator, create_simulator

# Global variable to store the current simulator
current_simulator = None


def get_current_simulator() -> Optional[Simulator]:
    """Get the current active simulator instance."""
    global current_simulator
    return current_simulator


def set_current_simulator(simulator: Optional[Simulator]) -> None:
    """Set the current active simulator instance."""
    global current_simulator
    current_simulator = simulator


class CreateSimulatorTool(Tool):
    name = "create_simulator"
    description = """
    Initialize a simulator environment.
    Creates a new simulation environment of the specified type with the given parameters.
    """
    inputs = {
        "simulator_type": {
            "type": "string",
            "description": (
                f"Type of simulator to initialize ({SimulationType.TowerOfHanoi.name} "
                f"or {SimulationType.RiverCrossing.name})"
            ),
        },
        "N": {
            "type": "integer",
            "description": "Size parameter defining the scale of the simulation",
        },
        "k": {
            "type": "integer",
            "description": (
                f"For {SimulationType.RiverCrossing.name}, the maximum number of "
                "passengers the boat can carry"
            ),
            "optional": True,
            "nullable": True,
        },
    }
    output_type = "object"

    def forward(self, simulator_type: str, N: int, k: Optional[int] = None) -> Dict[str, Any]:
        f"""
        Initialize a simulator environment.

        Args:
            simulator_type: Type of simulator to initialize ({SimulationType.TowerOfHanoi.name} or
                            {SimulationType.RiverCrossing.name})
            N: Size parameter defining the scale of the simulation
            k: For {SimulationType.RiverCrossing.name}, the maximum number of passengers the boat 
               can carry

        Returns:
            Dictionary containing simulator type and parameters
        """
        if simulator_type not in [t.name for t in SimulationType]:
            return {
                "error": (f"Invalid simulator type. Must be in '{[t.name for t in SimulationType]}")
            }

        simulator_type = SimulationType[simulator_type]

        if N < 1:
            return {"error": "N must be at least 1"}

        if k is not None and k < 1:
            return {"error": "k must be at least 1"}

        params = {"N": N}
        if k is not None:
            params["k"] = k

        try:
            simulator = create_simulator(simulator_type, params)
            set_current_simulator(simulator)
            return {
                "simulator_type": simulator.type.name,
                "simulator_params": simulator.params,
            }
        except ValueError as e:
            return {"error": str(e)}


class ResetSimulatorTool(Tool):
    name = "reset_simulator"
    description = """
    Reset a simulator to its initial state or to a provided state.
    This allows restarting the simulation or setting it to a specific configuration.
    """
    inputs = {
        "state": {
            "type": "any",
            "description": f"""
            Optional state to reset to. If not provided, reset to default initial state.
            Can be one of:
            - {SimulationType.TowerOfHanoi.name} state: List of 3 lists
            - {SimulationType.RiverCrossing.name} state: [boat_position, entity_positions]
            - "default" or None: Reset to default initial state
            """,
            "optional": True,
            "nullable": True,
        },
    }
    output_type = "object"

    def forward(
        self,
        state: Union[List[List[int]], List[Union[int, Dict[str, int]]], str, None] = None,
    ) -> Dict[str, Any]:
        """
        Reset a simulator to its initial state or to a provided state.

        Args:
            state: Optional state to reset to. If not provided, reset to default initial state.

        Returns:
            Dictionary indicating reset success and current state
        """
        simulator = get_current_simulator()

        if simulator is None:
            return {"error": "No simulator has been initialized"}

        try:
            # Check if state is "default" or None, in which case we reset to default state
            if state is None or state == "default":
                simulator.reset()
            else:
                # Let the simulator handle validation by attempting to reset with the provided state
                simulator.reset(state)

            return {"reset_successful": True, "current_state": simulator.state}
        except ValueError as e:
            return {"error": str(e), "reset_successful": False}


class GetStateTool(Tool):
    name = "get_state"
    description = """
    Get the current state of the simulator.
    Returns detailed information about the current configuration of the simulation.
    """
    inputs = {}
    output_type = "object"

    def forward(self) -> Dict[str, Any]:
        """
        Get the current state of the simulator.

        Returns:
            Dictionary containing current state and goal status
        """
        simulator = get_current_simulator()

        if simulator is None:
            return {"error": "No simulator has been initialized"}

        return {
            "simulator_type": simulator.type.name,
            "simulator_params": simulator.params,
            "state": simulator.state,
            "goal_reached": simulator.is_goal_reached(),
        }


class ExecuteMovesTool(Tool):
    name = "execute_moves"
    description = """
    Execute multiple moves in sequence in the simulation.
    Allows executing a series of moves and returns the final state.
    """
    inputs = {
        "moves": {
            "type": "array",
            "description": f"""
            List of moves to execute in sequence.
            - For {SimulationType.TowerOfHanoi.name}: [[disk_id, from_peg, to_peg], ...]
            - For {SimulationType.RiverCrossing.name}: [["A_1", "a_1"], ...]
            """,
        },
    }
    output_type = "object"

    def forward(self, moves: List[Any]) -> Dict[str, Any]:
        """
        Execute multiple moves in sequence in the simulation.

        Args:
            moves: List of moves to execute in sequence

        Returns:
            Dictionary containing results of each move, final state, and goal status
        """
        simulator = get_current_simulator()

        if simulator is None:
            return {"error": "No simulator has been initialized"}

        move_results = []
        for i, move in enumerate(moves):
            move_was_successful = simulator.execute_move(move)
            move_results.append({"move_index": i, "move": move, "successful": move_was_successful})

            if not move_was_successful:
                break

        state = simulator.state
        goal_reached = simulator.is_goal_reached()

        return {
            "move_results": move_results,
            "final_state": state,
            "goal_reached": goal_reached,
            "all_moves_successful": all(result["successful"] for result in move_results),
        }
