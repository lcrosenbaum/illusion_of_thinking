"""
Model Context Protocol (MCP) server for simulator environments.

This module implements an MCP server that provides a protocol for interacting
with various simulator environments.
"""

import logging
import time
import uuid
from typing import Any, Dict, List, Optional, Union

from fastmcp import FastMCP

from illusion_of_thinking.simulators import (
    RiverCrossingSimulator,
    Simulator,
    TowerOfHanoiSimulator,
    create_simulator,
)

# --- Configure Logging ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class SimulationEnvironment:
    """A simulation environment that holds a simulator instance and its metadata."""

    def __init__(self, simulator_type: str, simulator_params: Dict[str, Any]):
        """Initialize a simulation environment with a specific simulator type and parameters."""
        self.simulator = create_simulator(simulator_type, simulator_params)
        self.id = str(uuid.uuid4())
        self.last_accessed = time.time()  # Add timestamp for tracking last access

    @property
    def simulator_type(self) -> str:
        """Get the type of the simulator."""
        return self.simulator.type

    @property
    def simulator_params(self) -> Dict[str, Any]:
        """Get the parameters of the simulator."""
        return self.simulator.params


class SimulationManager:
    """Manager for simulation environments."""

    def __init__(self):
        """Initialize the simulation manager."""
        self.environments: Dict[str, SimulationEnvironment] = {}
        self.inactive_threshold: int = 180  # Two minutes in seconds

    def create_environment(
        self, simulator_type: str, simulator_params: Dict[str, Any]
    ) -> SimulationEnvironment:
        """Create a new simulation environment and register it."""
        # Clean up inactive environments
        self.cleanup_inactive_environments()

        env = SimulationEnvironment(simulator_type, simulator_params)
        self.environments[env.id] = env
        return env

    def get_environment(self, env_id: str) -> Optional[SimulationEnvironment]:
        """Get a simulation environment by ID and update its last accessed timestamp."""
        env = self.environments.get(env_id)
        if env:
            env.last_accessed = time.time()  # Update timestamp when accessed
        return env

    def validate_environment(self, env_id: str) -> bool:
        """Validate if the environment exists."""
        return env_id in self.environments

    def delete_environment(self, env_id: str) -> bool:
        """Delete a simulation environment."""
        if env_id in self.environments:
            del self.environments[env_id]
            return True
        return False

    def cleanup_inactive_environments(self) -> None:
        """Remove environments that haven't been accessed for more than the inactive threshold."""
        current_time = time.time()
        inactive_envs = [
            env_id
            for env_id, env in self.environments.items()
            if current_time - env.last_accessed > self.inactive_threshold
        ]

        for env_id in inactive_envs:
            logger.info(f"Cleaning up inactive environment: {env_id}")
            self.delete_environment(env_id)


# Create a single global instance of the FastMCP server
mcp = FastMCP(name="SimulationServer")

# Create a global simulation manager
simulation_manager = SimulationManager()


@mcp.tool
def init_simulator(simulator_type: str, N: int, k: Optional[int] = None) -> Dict[str, Any]:
    """
    Initialize a simulator environment.

    Args:
        simulator_type: Type of simulator to initialize (TowerOfHanoi or RiverCrossing)
        N: Size parameter defining the scale of the simulation
        k: For RiverCrossing, the maximum number of passengers the boat can carry

    Returns:
        Dictionary containing environment ID, token, simulator type, and parameters
    """
    if simulator_type not in [TowerOfHanoiSimulator.type, RiverCrossingSimulator.type]:
        return {
            "error": f"Invalid simulator type. Must be '{TowerOfHanoiSimulator.type}' or '{RiverCrossingSimulator.type}'"
        }

    if N < 1:
        return {"error": "N must be at least 1"}

    if k is not None and k < 1:
        return {"error": "k must be at least 1"}

    logger.info(f"Initializing {simulator_type} simulator with N={N} and k={k}")

    simulator_params = {"N": N}
    if k is not None:
        simulator_params["k"] = k

    environment = simulation_manager.create_environment(simulator_type, simulator_params)

    return {
        "env_id": environment.id,
        "simulator_type": environment.simulator_type,
        "simulator_params": environment.simulator_params,
    }


@mcp.tool
def execute_moves(env_id: str, moves: Union[List[List[int]], List[List[str]]]) -> Dict[str, Any]:
    """
    Execute aa list of moves in the simulation.

    Args:
        env_id: Environment ID of the simulator
        move: The move to execute in the simulator, which can be either:
              - For TowerOfHanoi: [disk_id, from_peg, to_peg]
              - For RiverCrossing: List of strings representing actors and agents

    Returns:
        Dictionary containing move success status, current state, and goal status
    """
    # Validate environment
    environment = simulation_manager.get_environment(env_id)
    if environment is None:
        return {"error": "Environment not found"}

    simulator = environment.simulator

    move_results = []
    for i, move in enumerate(moves):
        # Convert move to appropriate type if necessary
        move_was_successful = False
        if (
            isinstance(simulator, TowerOfHanoiSimulator)
            and isinstance(move, list)
            and len(move) == 3
        ):
            # Convert to tuple for TowerOfHanoi
            move_tuple = tuple(move)
            move_was_successful = simulator.execute_move(move_tuple)
        else:
            move_was_successful = simulator.execute_move(move)

        move_results.append({"move_index": i, "move": move, "successful": move_was_successful})

        # Stop execution if a move fails
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


@mcp.tool
def reset_simulator(
    env_id: str,
    state: Union[List[List[int]], List[Union[int, Dict[str, int]]], str, None] = None,
) -> Dict[str, Any]:
    """
    Reset a simulator to its initial state or to a provided state.

    Args:
        env_id: Environment ID of the simulator
        state: Optional state to reset to. If not provided, reset to default initial state.
               Can be one of:
               - TowerOfHanoi state: List of 3 lists
               - RiverCrossing state: [boat_position, entity_positions]
               - "default" or None: Reset to default initial state

    Returns:
        Dictionary indicating reset success and current state
    """
    # Validate environment
    environment = simulation_manager.get_environment(env_id)
    if environment is None:
        return {"error": "Environment not found"}

    try:
        # Check if state is "default" or None, in which case we reset to default state
        if state is None or state == "default":
            environment.simulator.reset()
        else:
            # Let the simulator handle validation by attempting to reset with the provided state
            environment.simulator.reset(state)

        return {"reset_successful": True, "current_state": environment.simulator.state}
    except ValueError as e:
        return {"error": str(e), "reset_successful": False}


@mcp.tool
def get_state(env_id: str) -> Dict[str, Any]:
    """
    Get the current state of a simulator.

    Args:
        env_id: Environment ID of the simulator

    Returns:
        Dictionary containing simulator type, parameters, current state, and goal status
    """
    # Validate environment ID
    environment = simulation_manager.get_environment(env_id)
    if environment is None:
        return {"error": "Environment not found"}

    return {
        "simulator_type": environment.simulator_type,
        "simulator_params": environment.simulator_params,
        "state": environment.simulator.state,
        "goal_reached": environment.simulator.is_goal_reached(),
    }


if __name__ == "__main__":
    mcp.run()  # Use the default stdio transport
