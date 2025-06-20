# Simulator Tools

This document describes the tools provided in `simulator_tools.py` for interacting with simulation environments in the Illusion of Thinking project.

## Overview

The simulator tools provide a structured interface for creating, resetting, querying, and manipulating simulation environments. These tools are designed to be used programmatically, for example in agent frameworks or automated workflows.

## Available Tools

### 1. CreateSimulatorTool

- **Purpose:** Initialize a new simulator environment of a specified type (`TowerOfHanoi` or `RiverCrossing`) with given parameters.
- **Inputs:** 
  - `simulator_type` (string): Type of simulator to initialize.
  - `N` (integer): Size parameter.
  - `k` (integer, optional): For RiverCrossing, the boat capacity.
- **Output:** Simulator type and parameters, or error message.

### 2. ResetSimulatorTool

- **Purpose:** Reset the simulator to its initial state or to a provided state.
- **Inputs:** 
  - `state` (any, optional): State to reset to, or "default"/None for initial state.
- **Output:** Reset status and current state, or error message.

### 3. GetStateTool

- **Purpose:** Retrieve the current state and goal status of the simulator.
- **Inputs:** None.
- **Output:** Simulator type, parameters, current state, and goal status.

### 4. ExecuteMovesTool

- **Purpose:** Execute a sequence of moves in the simulator.
- **Inputs:** 
  - `moves` (array): List of moves to execute.
- **Output:** Results for each move, final state, goal status, and overall success.

## Usage

These tools are implemented as classes and can be integrated into agent workflows or called directly in Python code. Only one simulator is active at a time in this simplified interface.

See the code in `simulator_tools.py` for implementation details.
