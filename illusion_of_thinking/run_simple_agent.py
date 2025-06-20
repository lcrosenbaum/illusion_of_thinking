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

from illusion_of_thinking.constants import SimulationType
from illusion_of_thinking.prompts import get_prompts
from illusion_of_thinking.simulator_tools import (
    CreateSimulatorTool,
    ExecuteMovesTool,
    GetStateTool,
    ResetSimulatorTool,
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
        choices=[t.name for t in SimulationType],
        default=SimulationType.TowerOfHanoi.name,
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

    # Convert string simulator_type to SimulationType enum
    simulator_enum = SimulationType[args.simulator_type]

    # Get prompts based on simulator type and parameters
    prompts = get_prompts(
        simulator_type=simulator_enum,
        N=args.N,
        k=args.k if simulator_enum == SimulationType.RiverCrossing else None,
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
