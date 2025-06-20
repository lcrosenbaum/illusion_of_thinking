from .constants import SimulationType

USER_PROMPT_TEMPLATES = {
    SimulationType.TowerOfHanoi: (
        "I have a puzzle with $N={N}$ disks of different sizes with\n"
        "**Initial configuration:**\n"
        "- Peg 0: $N={N}$ (bottom), . . . 2, 1 (top)\n"
        "- Peg 1: (empty)\n"
        "- Peg 2: (empty)\n"
        "**Goal configuration:**\n"
        "- Peg 0: (empty)\n"
        "- Peg 1: (empty)\n"
        "- Peg 2: $N={N}$ (bottom), . . . 2, 1 (top)\n"
        "**Rules:**\n"
        "- Only one disk can be moved at a time.\n"
        "- Only the top disk from any stack can be moved.\n"
        "- A larger disk may not be placed on top of a smaller disk.\n"
        "Find the sequence of moves to transform the initial configuration into the goal "
        "configuration."
    ),
    SimulationType.RiverCrossing: (
        "$N={N}$ actors and their $N={N}$ agents want to cross a river in a boat that is "
        "capable of holding only $k={k}$ people at a time, with the constraint that no "
        "actor can be in the presence of another agent, including while riding the boat, "
        "unless their own agent is also present, because each agent is worried their "
        "rivals will poach their client. Initially, all actors and agents are on the "
        "left side of the river with the boat. How should they cross the river?"
    ),
}

SYSTEM_PROMPT_TEMPLATES = {
    SimulationType.TowerOfHanoi: (
        "You are a helpful assistant. Solve this puzzle for me.\n"
        "There are three pegs and n disks of different sizes stacked on the first peg. The "
        "disks are numbered from 1 (smallest) to n (largest). Disk moves in this puzzle "
        "should follow:\n "
        "1. Only one disk can be moved at a time. n "
        "2. Each move consists of taking the upper disk from one stack and placing it on top of "
        "another stack.\n "
        "3. A larger disk may not be placed on top of a smaller disk.\n "
        "The goal is to move the entire stack to the third peg.\n "
        "**Example:** With 3 disks numbered 1 (smallest), 2, and 3 (largest), the initial state is "
        "[[3, 2, 1], [], []], and a solution might be:\n "
        "moves = [[1 , 0 , 2] , [2 , 0 , 1] , [1 , 2 , 1] , [3 , 0 , 2] , "
        "[1 , 1 , 0] , [2 , 1 , 2] , [1 , 0 , 2]]\n "
        "This means: Move disk 1 from peg 0 to peg 2, then move disk 2 from peg 0 to peg 1, and so "
        "on.\n "
        "**Requirements:**\n "
        "- When exploring potential solutions in your thinking process, always include the "
        "corresponding complete list of moves.\n "
        "- The positions are 0-indexed (the leftmost peg is 0).\n "
        "- Ensure your final answer includes the complete list of moves in the format:\n "
        "moves = [[disk id, from peg, to peg], ...]\n "
    ),
    SimulationType.RiverCrossing: (
        "You are a helpful assistant. Solve this puzzle for me.\n"
        "You can represent actors with a_1, a_2, ... and agents with A_1, A_2, ... . "
        "Your solution must be a list of boat moves where each move indicates the people "
        "on the boat. For example, if there were two actors and two agents, you should return:\n"
        'moves =[[" A_2 ", " a_2 "] , [" A_2 "] , [" A_1 " , " A_2 "] , [" A_1 "] , [" A_1 " , '
        '" a_1 "]]\n'
        "which indicates that in the first move, A_2 and a_2 row from left to right, and in the "
        "second move, A_2 rows from right to left and so on.\n"
        "**Requirements**:\n"
        "- When exploring potential solutions in your thinking process, always include the "
        " corresponding complete list of boat moves.\n"
        "- The list shouldn’t have comments.\n"
    ),
}


def get_prompts(simulator_type: SimulationType, **kwargs) -> dict:
    """
    Get formatted prompt templates for the specified simulator type.

    Args:
        simulator_type: The type of simulator (from SimulationType enum)
        **kwargs: Parameters used to format the prompt templates (e.g., N, k)

    Returns:
        dict: Dictionary containing formatted user and system prompts
    """
    # Get the appropriate templates
    user_prompt_template = USER_PROMPT_TEMPLATES.get(simulator_type, "")
    system_prompt_template = SYSTEM_PROMPT_TEMPLATES.get(simulator_type, "")

    # Format the templates with the provided kwargs
    user_prompt = user_prompt_template.format(**kwargs) if user_prompt_template else ""
    system_prompt = system_prompt_template.format(**kwargs) if system_prompt_template else ""

    return {"user_prompt": user_prompt, "system_prompt": system_prompt}
