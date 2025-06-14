import asyncio
import json
import os
import pathlib
from typing import Any, Dict, List, Tuple

import pytest
import pytest_asyncio
from fastmcp import Client


@pytest_asyncio.fixture
async def client():
    """Fixture that creates a connected client using stdio transport."""
    # Get the absolute path to the server script by resolving it relative to this test file
    current_dir = pathlib.Path(__file__).parent
    server_path = str(current_dir.parent / "illusion_of_thinking" / "mcp_server.py")

    # Verify the file exists before trying to create a client
    if not os.path.exists(server_path):
        raise FileNotFoundError(f"Server script not found at: {server_path}")

    # Connect to the script file using absolute path
    client = Client(server_path)
    async with client:
        yield client


def result_as_dict(result: Any) -> Dict[str, Any]:
    """Helper function to convert result to a dictionary."""
    if isinstance(result, list) and len(result) == 1:
        result = result[0]  # Extract the first result item
        if hasattr(result, "text"):
            try:
                return json.loads(result.text)
            except json.JSONDecodeError:
                return {"text": result.text}

    # For direct tool results
    if hasattr(result, "content"):
        try:
            return json.loads(result.content)
        except (json.JSONDecodeError, AttributeError, TypeError):
            if isinstance(result.content, dict):
                return result.content
            return {"content": result.content}

    # Return the result as is if we can't process it
    return result


async def call_tool(client: Client, tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Wrapper function to call a tool and convert the result to a dictionary."""
    result = await client.call_tool(tool_name, args)
    return result_as_dict(result)


@pytest.mark.asyncio
async def test_init_simulator(client):
    """Test initializing a Tower of Hanoi simulator."""
    # Initialize a Tower of Hanoi simulator
    result = await call_tool(client, "init_simulator", {"simulator_type": "TowerOfHanoi", "N": 3})

    assert "env_id" in result
    assert result["simulator_type"] == "TowerOfHanoi"
    assert result["simulator_params"] == {"N": 3}


@pytest.mark.asyncio
async def test_init_river_crossing(client):
    """Test initializing a River Crossing simulator."""
    # Initialize a River Crossing simulator
    result = await call_tool(
        client, "init_simulator", {"simulator_type": "RiverCrossing", "N": 2, "k": 2}
    )

    assert "env_id" in result
    assert result["simulator_type"] == "RiverCrossing"
    assert result["simulator_params"] == {"N": 2, "k": 2}

    # Verify the environment exists by checking state resource
    env_id = result["env_id"]
    state_data = await call_tool(client, "get_state", {"env_id": env_id})
    assert state_data["simulator_type"] == "RiverCrossing"
    assert state_data["simulator_params"] == {"N": 2, "k": 2}
    assert state_data["goal_reached"] is False


@pytest.mark.asyncio
async def test_init_hanoi(client):
    """Test initializing a River Crossing simulator."""
    # Initialize a River Crossing simulator
    result = await call_tool(client, "init_simulator", {"simulator_type": "TowerOfHanoi", "N": 2})

    assert "env_id" in result
    assert result["simulator_type"] == "TowerOfHanoi"
    assert result["simulator_params"] == {"N": 2}

    # Verify the environment exists by checking state resource
    env_id = result["env_id"]
    state_data = await call_tool(client, "get_state", {"env_id": env_id})
    assert state_data["simulator_type"] == "TowerOfHanoi"
    assert state_data["simulator_params"] == {"N": 2}
    assert state_data["goal_reached"] is False


@pytest.mark.asyncio
async def test_init_simulator_validation(client):
    """Test validation when initializing a simulator."""
    # Test with invalid simulator type
    result = await call_tool(client, "init_simulator", {"simulator_type": "InvalidType", "N": 3})
    assert "error" in result
    assert "Invalid simulator type" in result["error"]

    # Test with invalid N value
    result = await call_tool(client, "init_simulator", {"simulator_type": "TowerOfHanoi", "N": 0})
    assert "error" in result
    assert "N must be at least 1" in result["error"]

    # Test with invalid k value
    result = await call_tool(
        client, "init_simulator", {"simulator_type": "RiverCrossing", "N": 2, "k": 0}
    )
    assert "error" in result
    assert "k must be at least 1" in result["error"]


@pytest.mark.asyncio
async def test_execute_moves_tower_of_hanoi(client):
    """Test executing a move in the Tower of Hanoi simulator."""
    # Initialize a Tower of Hanoi simulator
    init_result = await call_tool(
        client, "init_simulator", {"simulator_type": "TowerOfHanoi", "N": 3}
    )
    env_id = init_result["env_id"]

    # Execute a valid move: move disk 1 from peg 0 to peg 2
    move_result = await call_tool(
        client, "execute_moves", {"env_id": env_id, "moves": [[1, 0, 2], [2, 0, 1]]}
    )

    assert move_result["all_moves_successful"]
    assert not move_result["goal_reached"]
    assert isinstance(move_result["final_state"], list)  # State should be a tuple of lists
    assert len(move_result["final_state"]) == 3  # 3 pegs
    assert 3 in move_result["final_state"][0]
    assert 2 in move_result["final_state"][1]
    assert 1 in move_result["final_state"][2]


@pytest.mark.asyncio
async def test_execute_moves_river_crossing(client):
    """Test executing a move in the River Crossing simulator."""
    # Initialize a River Crossing simulator
    init_result = await call_tool(
        client, "init_simulator", {"simulator_type": "RiverCrossing", "N": 2, "k": 2}
    )
    env_id = init_result["env_id"]

    # Execute a valid move: move actor a_1 and agent A_1 to other side
    move_result = await call_tool(
        client, "execute_moves", {"env_id": env_id, "moves": [["a_1", "A_1"]]}
    )

    assert move_result["all_moves_successful"]
    assert isinstance(move_result["final_state"], list) or isinstance(
        move_result["final_state"], tuple
    )
    # Check that boat position changed to 1 (right side)
    assert move_result["final_state"][0] == 1
    # Check that actor a_1 and agent A_1 are now on the right side (1)
    entity_positions = move_result["final_state"][1]
    assert entity_positions["a_1"] == 1
    assert entity_positions["A_1"] == 1


@pytest.mark.asyncio
async def test_execute_moves_validation(client):
    """Test validation when executing a move."""
    # Initialize a Tower of Hanoi simulator
    init_result = await call_tool(
        client, "init_simulator", {"simulator_type": "TowerOfHanoi", "N": 3}
    )
    env_id = init_result["env_id"]

    # Test with invalid env_id
    result = await call_tool(
        client, "execute_moves", {"env_id": "invalid_id", "moves": [[1, 0, 2]]}
    )
    assert "error" in result
    assert "Environment not found" in result["error"]

    # Test with invalid move (moving disk from empty peg)
    result = await call_tool(
        client,
        "execute_moves",
        {"env_id": env_id, "moves": [[1, 1, 2]]},  # Peg 1 is empty at the start
    )
    assert result["all_moves_successful"] is False


@pytest.mark.asyncio
async def test_reset_simulator(client):
    """Test resetting a simulator."""
    # Initialize a Tower of Hanoi simulator
    init_result = await call_tool(
        client, "init_simulator", {"simulator_type": "TowerOfHanoi", "N": 3}
    )
    env_id = init_result["env_id"]

    # Make a move
    await call_tool(client, "execute_moves", {"env_id": env_id, "moves": [[1, 0, 2]]})

    # Reset to default state
    reset_result = await call_tool(client, "reset_simulator", {"env_id": env_id, "state": None})

    assert reset_result["reset_successful"] is True
    # After reset, all disks should be on the first peg
    state = reset_result["current_state"]
    assert len(state[0]) == 3  # 3 disks on first peg
    assert len(state[1]) == 0  # 0 disks on second peg
    assert len(state[2]) == 0  # 0 disks on third peg


@pytest.mark.asyncio
async def test_reset_simulator_custom_state(client):
    """Test resetting a simulator to a custom state."""
    # Initialize a Tower of Hanoi simulator
    init_result = await call_tool(
        client, "init_simulator", {"simulator_type": "TowerOfHanoi", "N": 3}
    )
    env_id = init_result["env_id"]

    # Reset to a custom state
    custom_state = [[3, 2], [1], []]  # Disk 1 on peg 1, others on peg 0
    reset_result = await call_tool(
        client, "reset_simulator", {"env_id": env_id, "state": custom_state}
    )

    assert reset_result["reset_successful"] is True
    state = reset_result["current_state"]
    assert state[0] == [3, 2]  # Disks 3 and 2 on first peg
    assert state[1] == [1]  # Disk 1 on second peg
    assert state[2] == []  # No disks on third peg


@pytest.mark.asyncio
async def test_reset_simulator_validation(client):
    """Test validation when resetting a simulator."""
    # Initialize a Tower of Hanoi simulator
    init_result = await call_tool(
        client, "init_simulator", {"simulator_type": "TowerOfHanoi", "N": 3}
    )
    env_id = init_result["env_id"]

    # Test with invalid env_id
    result = await call_tool(client, "reset_simulator", {"env_id": "invalid_id", "state": None})
    assert "error" in result
    assert "Environment not found" in result["error"]

    # Test with invalid state format
    result = await call_tool(
        client,
        "reset_simulator",
        {
            "env_id": env_id,
            "state": "invalid_state",  # Not None or "default", and not a valid state list
        },
    )
    assert "error" in result
    assert result["reset_successful"] is False


@pytest.mark.asyncio
async def test_state_resource(client):
    """Test accessing the state resource."""
    # Initialize a Tower of Hanoi simulator
    init_result = await call_tool(
        client, "init_simulator", {"simulator_type": "TowerOfHanoi", "N": 3}
    )
    env_id = init_result["env_id"]

    # Access the state resource
    state_data = await call_tool(client, "get_state", {"env_id": env_id})

    assert state_data["simulator_type"] == "TowerOfHanoi"
    assert state_data["simulator_params"] == {"N": 3}
    assert isinstance(state_data["state"], list)  # State will be serialized as a list of lists
    assert len(state_data["state"]) == 3  # 3 pegs
    assert state_data["goal_reached"] is False


@pytest.mark.asyncio
async def test_state_resource_validation(client):
    """Test validation when accessing the state resource."""
    # Initialize a simulator
    init_result = await call_tool(
        client, "init_simulator", {"simulator_type": "TowerOfHanoi", "N": 3}
    )

    # Test with invalid env_id
    state_data = await call_tool(client, "get_state", {"env_id": "invalid_id"})
    assert "error" in state_data
    assert "Environment not found" in state_data["error"]
