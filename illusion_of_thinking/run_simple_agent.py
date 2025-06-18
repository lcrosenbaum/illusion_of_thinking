"""
A Puzzle Agent that uses simulator tools to solve puzzles.

This agent provides a way to interact with simulation puzzles using LLM-based agents.
"""

import argparse
import os
from typing import Any, Dict, List, Optional, Union

from smolagents import (
    EMPTY_PROMPT_TEMPLATES,
    LiteLLMModel,
    LogLevel,
    Message,
    Tool,
    ToolCallingAgent,
)

from illusion_of_thinking.simulator_tools import (
    CreateSimulatorTool,
    ExecuteMovesTool,
    GetStateTool,
    ResetSimulatorTool,
)


def get_prompts(simulator_type: str, use_tools: bool, **kwargs) -> str:
    if simulator_type == "TowerOfHanoi":
        N = kwargs.get("N", 3)
        user_prompt = (
            f"I have a puzzle with $N={N}$ disks of different sizes with\n"
            "Initial configuration:\n"
            f"* Peg 0: $N={N}$ (bottom), . . . 2, 1 (top)\n"
            "* Peg 1: (empty)\n"
            "* Peg 2: (empty)\n"
            "Goal configuration:\n"
            "* Peg 0: (empty)\n"
            "* Peg 1: (empty)\n"
            f"* Peg 2: $N={N}$ (bottom), . . . 2, 1 (top)\n"
            "Rules:\n"
            "* Only one disk can be moved at a time.\n"
            "* Only the top disk from any stack can be moved.\n"
            "* A larger disk may not be placed on top of a smaller disk.\n"
            "Find the sequence of moves to transform the initial configuration into the goal configuration."
        )
        system_prompt = (
            "You are a helpful assistant. Solve this puzzle for me.\n"
            "There are three pegs and n disks of different sizes stacked on the first peg. The "
            "disks are numbered from 1 (smallest) to n (largest). Disk moves in this puzzle "
            "should follow:\n "
            "1. Only one disk can be moved at a time. n "
            "2. Each move consists of taking the upper disk from one stack and placing it on top of "
            "another stack.\n "
            "3. A larger disk may not be placed on top of a smaller disk.\n "
            "The goal is to move the entire stack to the third peg.\n "
            "Example: With 3 disks numbered 1 (smallest), 2, and 3 (largest), the initial state is "
            "[[3, 2, 1], [], []], and a solution might be:\n "
            "moves = [[1 , 0 , 2] , [2 , 0 , 1] , [1 , 2 , 1] , [3 , 0 , 2] , "
            "[1 , 1 , 0] , [2 , 1 , 2] , [1 , 0 , 2]]\n "
            "This means: Move disk 1 from peg 0 to peg 2, then move disk 2 from peg 0 to peg 1, and so on.\n "
            "Requirements:\n "
            "* When exploring potential solutions in your thinking process, always include the corresponding complete list of moves.\n "
            "* The positions are 0-indexed (the leftmost peg is 0).\n "
            "* Ensure your final answer includes the complete list of moves in the format:\n "
            "moves = [[disk id, from peg, to peg], ...]\n "
        )

    elif simulator_type == "RiverCrossing":
        N = kwargs.get("N", 4)
        k = kwargs.get("k", 2)
        user_prompt = (
            f"$N={N}$ actors and their $N={N}$ agents want to cross a river in a boat that is "
            f"capable of holding only $k={k}$ people at a time, with the constraint that no "
            "actor can be in the presence of another agent, including while riding the boat, "
            "unless their own agent is also present, because each agent is worried their "
            "rivals will poach their client. Initially, all actors and agents are on the "
            "left side of the river with the boat. How should they cross the river?"
        )
        system_prompt = (
            "You are a helpful assistant. Solve this puzzle for me.\n"
            "You can represent actors with a_1, a_2, ... and agents with A_1, A_2, ... . "
            "Your solution must be a list of boat moves where each move indicates the people "
            "on the boat. For example, if there were two actors and two agents, you should return:\n"
            'moves =[[" A_2 ", " a_2 "] , [" A_2 "] , [" A_1 " , " A_2 "] , [" A_1 "] , [" A_1 " , " a_1 "]]\n'
            "which indicates that in the first move, A_2 and a_2 row from left to right, and in the second "
            "move, A_2 rows from right to left and so on.\n"
            "**Requirements**:\n"
            "* When exploring potential solutions in your thinking process, always include the corresponding complete list of boat moves.\n"
            "* The list shouldn’t have comments.\n"
        )
    else:
        user_prompt = ""
        system_prompt = ""

    if use_tools:
        system_prompt += (
            "**Simulator**:\n"
            "* You can use a simulator as tool to execute and explore a set of moves.\n"
            "* This means you can use a tool to set up or reset a simualtor to certain state, such that you can restart at a certain position.\n"
            "* You can also ask to execute and evaluate certain moves."
        )

    return dict(
        user_prompt=user_prompt,
        system_prompt=system_prompt,
    )


def get_tools() -> List[Tool]:
    return [
        CreateSimulatorTool(),
        GetStateTool(),
        ResetSimulatorTool(),
        ExecuteMovesTool(),
    ]


def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Run a puzzle-solving agent")
    parser.add_argument(
        "--simulator_type",
        type=str,
        choices=["TowerOfHanoi", "RiverCrossing"],
        default="TowerOfHanoi",
        help="Type of simulator to use",
    )
    parser.add_argument(
        "--N",
        type=int,
        default=3,
        help="Number of disks for Tower of Hanoi or number of actors for River Crossing",
    )
    parser.add_argument(
        "--k",
        type=int,
        default=2,
        help="Maximum boat capacity for River Crossing (ignored for Tower of Hanoi)",
    )
    parser.add_argument("--use_tools", action="store_true", help="Whether to use simulator tools")
    parser.add_argument(
        "--use_thinking", action="store_true", help="Whether to use a thinking model or not."
    )

    args = parser.parse_args()

    # Get prompts based on simulator type and parameters
    prompts = get_prompts(
        simulator_type=args.simulator_type, N=args.N, k=args.k, use_tools=args.use_tools
    )

    # Set up tools if requested
    tools = get_tools() if args.use_tools else []

    # Get client configuration for the selected model
    if args.use_thinking:
        model_id = "mistral/magistral-medium-2506"
    else:
        model_id = "mistral/mistral-medium-2505"  # Default to Mistral Large

    model = LiteLLMModel(
        model_id=model_id, temperature=1.0, max_tokens=40000, api_key=os.getenv("MISTRAL_API_KEY")
    )

    prompt_templates = EMPTY_PROMPT_TEMPLATES
    prompt_templates["system_prompt"] = prompts["system_prompt"]
    # Create the agent without system_message parameter
    agent = ToolCallingAgent(
        prompt_templates=prompt_templates, tools=tools, model=model, verbosity_level=LogLevel.DEBUG
    )

    response_gen = agent.run(prompts["user_prompt"], stream=True)

    for chunk in response_gen:
        pass


if __name__ == "__main__":
    main()
