import argparse
import importlib
import os
import pathlib
from typing import Dict

import yaml
from smolagents import (
    EMPTY_PROMPT_TEMPLATES,
    CodeAgent,
    FinalAnswerStep,
    LiteLLMModel,
    MultiStepAgent,
    ToolCallingAgent,
)

from illusion_of_thinking.constants import SimulationType
from illusion_of_thinking.simulator_tools import get_tools


def get_prompt_templates(simulator_type: SimulationType, **kwargs) -> Dict[str, str]:
    """
    Get formatted prompt templates for the specified simulator type. The
    function uses str.format() to fill in variables, but leaves jinja2 based
    templates untouched. This way the smolagents can replace the variables with
    correct tools and so on.

    Args:
        simulator_type: The type of simulator (from SimulationType enum)
        **kwargs: Parameters used to format the prompt templates (e.g., N, k)

    Returns:
        dict: Dictionary containing formatted user and system prompts
    """
    # Get the appropriate templates
    prompt_templates = yaml.safe_load(
        importlib.resources.files("illusion_of_thinking.prompts")
        .joinpath(f"{simulator_type.name}_original.yaml")
        .read_text()
    )

    for k, v in prompt_templates.items():
        prompt_templates[k] = v.format(**kwargs)

    return prompt_templates


def configure_agent(
    use_tools: bool = False,
    use_thinking: bool = False,
    use_code: bool = False,
    prompt_templates: Dict[str, str] = None,
) -> MultiStepAgent:
    """
    Configure the agent based on the provided parameters.
    Args:
        use_tools (bool): Whether to use tools for the agent.
        use_thinking (bool): Whether to use a thinking model.
        use_code (bool): Whether to use code execution.
        prompt_templates (Dict[str, str]): Custom prompt templates to use.
    Returns:
        MultiStepAgent: Configured agent instance.
    Raises:
        ValueError: If both tools and code execution are requested, or if neither is specified.
    """
    if use_code:
        raise ValueError("Code execution is not yet supported.")

    if use_tools:
        raise ValueError("Tool calling is not yet supported.")

    if use_tools and use_code:
        raise ValueError("Cannot use both tools and code execution at the same time.")

    tools = get_tools() if use_tools else []

    if use_thinking:
        model_id = "mistral/magistral-medium-2506"
    else:
        model_id = "mistral/mistral-medium-2505"

    model = LiteLLMModel(
        model_id=model_id, temperature=1.0, max_tokens=40000, api_key=os.getenv("MISTRAL_API_KEY")
    )

    if prompt_templates:
        prompt_templates_tmp = EMPTY_PROMPT_TEMPLATES
        prompt_templates_tmp.update(prompt_templates)
        prompt_templates = prompt_templates_tmp

    if use_tools:
        agent = ToolCallingAgent(
            prompt_templates=prompt_templates, tools=tools, model=model, verbosity_level=1
        )
    elif use_code:
        agent = CodeAgent(prompt_templates=prompt_templates, model=model, verbosity_level=1)
    else:
        agent = ToolCallingAgent(
            prompt_templates=prompt_templates, model=model, tools=[], verbosity_level=1
        )

    return agent


def main():
    parser = argparse.ArgumentParser(description="Run a puzzle-solving agent")
    parser.add_argument(
        "--simulator_type",
        type=str,
        choices=[t.name for t in SimulationType],
        help="Type of simulator to use",
        required=True,
    )
    parser.add_argument(
        "--N",
        type=int,
        help="Number of disks for Tower of Hanoi or number of actors for River Crossing",
        required=True,
    )
    parser.add_argument(
        "--k",
        type=int,
        default=2,
        help="Maximum boat capacity for River Crossing (ignored for Tower of Hanoi)",
    )
    parser.add_argument("--use_tools", action="store_true", help="Whether to use simulator tools.")
    parser.add_argument(
        "--use_thinking", action="store_true", help="Whether to use a thinking model or not."
    )
    parser.add_argument(
        "--use_code", action="store_true", help="Whether to allow the agent to use code or not."
    )
    parser.add_argument(
        "--output_folder",
        type=str,
        default="logs",
        help="Output folder for experiment_results.",
        required=True,
    )

    args = parser.parse_args()

    # Convert string simulator_type to SimulationType enum
    simulator_type = SimulationType[args.simulator_type]

    out_folder = f"{simulator_type.name}_N={args.N}"
    if simulator_type == SimulationType.RiverCrossing:
        out_folder += f"_k={args.k}"
    if args.use_thinking:
        out_folder += "_thinking"
    if args.use_tools:
        out_folder += "_tools"
    if args.use_code:
        out_folder += "_code"
    out_path = pathlib.Path(args.output_folder) / out_folder
    os.makedirs(out_path, exist_ok=True)

    # Get prompts based on simulator type and parameters
    prompts = get_prompt_templates(
        simulator_type=simulator_type,
        N=args.N,
        k=args.k if simulator_type == SimulationType.RiverCrossing else None,
    )

    agent = configure_agent(
        use_tools=args.use_tools,
        use_thinking=args.use_thinking,
        prompt_templates=prompts,
    )

    for i in range(10):
        with open(out_path / f"experiment_{i + 1}.yaml", "w") as f:
            print(f"Running experiment {i + 1}...")
            response = agent.run(prompts["user_prompt"])
            yaml.dump({"answer": response.to_string()}, f)


if __name__ == "__main__":
    main()
