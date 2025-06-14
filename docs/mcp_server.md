# Model Context Protocol (MCP) Server

## Overview

The Model Context Protocol (MCP) server provides a protocol for interacting with simulator environments. It exposes tools and resources for initializing, controlling, and querying the state of supported simulators.

## Supported Simulators
- **TowerOfHanoi**: Classic Tower of Hanoi puzzle (parameter: N = number of disks)
- **RiverCrossing**: River crossing puzzle (parameters: N = number of entities, k = boat capacity)

## Tools

### `init_simulator`
Initialize a simulator environment.
- **Arguments:**
  - `simulator_type`: "TowerOfHanoi" or "RiverCrossing"
  - `N`: Size parameter (int)
  - `k`: (Optional, int) For RiverCrossing only
- **Returns:**
  - `env_id`: Unique environment ID
  - `simulator_type`, `simulator_params`

### `execute_move`
Execute a move in the simulation.
- **Arguments:**
  - `env_id`: Environment ID
  - `move`: For TowerOfHanoi: [disk_id, from_peg, to_peg]; for RiverCrossing: list of actors/agents
- **Returns:**
  - `move_successful`, `state`, `goal_reached`

### `reset_simulator`
Reset a simulator to its initial or a provided state.
- **Arguments:**
  - `env_id`: Environment ID
  - `state`: (Optional) State to reset to, or "default"/None for initial state
- **Returns:**
  - `reset_successful`, `current_state`

### `get_state`
Get the current state of a simulator.
- **Arguments:**
  - `env_id`: Environment ID
- **Returns:**
  - `simulator_type`, `simulator_params`, `state`, `goal_reached`

## Example Client Usage

You can interact with the MCP server using the `fastmcp` client or any compatible MCP client. Here is a minimal example using Python:

```python
from fastmcp import MCPClient

client = MCPClient()

# Initialize a Tower of Hanoi simulator with 3 disks
resp = client.call_tool('init_simulator', simulator_type='TowerOfHanoi', N=3)
env_id = resp['env_id']

# Execute a move: move disk 1 from peg 0 to peg 2
move_result = client.call_tool('execute_move', env_id=env_id, move=[1, 0, 2])

# Reset the simulator
client.call_tool('reset_simulator', env_id=env_id)
```

## Running the Server

To start the server:

```bash
python -m illusion_of_thinking.mcp_server
```

The server uses stdio transport by default. For advanced usage, see the FastMCP documentation.

## Notes
- Inactive environments are automatically cleaned up after 2 minutes of inactivity.
- All tools return error messages in the response if invalid arguments are provided.
