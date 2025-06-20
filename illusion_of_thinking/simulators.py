from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union

from .constants import SimulationType


class Simulator(ABC):
    """
    Abstract base class for simulators.

    A simulator maintains the rules of a system, validates states and executes moves.
    """

    type = "base"  # Base type identifier

    def __init__(self, N: int):
        """
        Initialize the simulator with size parameter N.

        Args:
            N: Integer size parameter defining the scale of the simulation.
        """
        self.N = N
        self.state = None
        self.reset()

    @property
    def params(self) -> Dict[str, Any]:
        """
        Get the parameters used to initialize this simulator.

        Returns:
            Dictionary of parameters
        """
        return {"N": self.N}

    @abstractmethod
    def execute_move(self, move: Any) -> bool:
        """
        Execute a move from the current state and update the state.

        Note: It is assumed that the move starts from a valid state. A move is successful
        if the move is valid and the state after the move is valid.

        Args:
            move: The move to execute

        Returns:
            True if the move was successful, False otherwise
        """
        pass

    @abstractmethod
    def is_valid_state(self) -> bool:
        """
        Check if the current state is valid according to the simulator's rules.

        Note: A move is valid if it can be executed from the current state. It does not
        need to result in a valid state afterwards. But for some simulators this is checked.

        Returns:
            True if the state is valid, False otherwise
        """
        pass

    @abstractmethod
    def is_valid_move(self, move: Any) -> bool:
        """
        Check if a move is valid from the current state.

        Args:
            move: The move to validate

        Returns:
            True if the move is valid, False otherwise
        """
        pass

    @abstractmethod
    def reset(self, state: Optional[Any] = None) -> None:
        """
        Reset the simulator to the initial state or to a provided state.

        Args:
            state: Optional state to reset to. If None, reset to default initial state.
        """
        pass

    @abstractmethod
    def is_goal_reached(self) -> bool:
        """
        Check if the current state is a goal state.

        Returns:
            True if the goal has been reached, False otherwise
        """
        pass


class TowerOfHanoiSimulator(Simulator):
    """
    A simulator for the Tower of Hanoi puzzle.

    The Tower of Hanoi is a puzzle with $N$ disks of different sizes with
    initial configuration:
    - Peg 0: $N$ (bottom), . . . 2, 1 (top)
    - Peg 1: (empty)
    - Peg 2: (empty)

    Goal configuration:
    - Peg 0: (empty)
    - Peg 1: (empty)
    - Peg 2: $N$ (bottom), . . . 2, 1 (top)

    Rules:
    - Only one disk can be moved at a time.
    - Only the top disk from any stack can be moved.
    - A larger disk may not be placed on top of a smaller disk.

    A move is a tuple (disk_id, from_peg, to_peg) where pegs are indexed 0, 1, 2
    and disk_id is 1, ..., $N$ of the disk being moved. The disk_id goes from
    1 (smallest) to $N$ (largest), where the smallest disk is on top of the stack.
    """

    type = SimulationType.TowerOfHanoi

    def __init__(self, N: int):
        super().__init__(N)

    def reset(
        self, state: Optional[Union[Tuple[List[int], List[int], List[int]], List[List[int]]]] = None
    ) -> None:
        """
        Reset the Tower of Hanoi puzzle to its initial state or to a provided state.
        All disks on the first peg by default.

        Args:
            state: Optional state to reset to. If None, reset to default initial state.
                  Can be either a Tuple or a List of lists representing the pegs

        Raises:
            ValueError: If the provided state is not valid.
        """
        if state is not None:
            old_state = self.state
            # Cast list to tuple if needed
            if isinstance(state, list):
                state = tuple(state)
            self.state = state
            if not self.is_valid_state():
                self.state = old_state
                raise ValueError("Provided state is not a valid Tower of Hanoi state.")
        else:
            # Create initial state with all disks on the first peg
            # Order: largest disk (N) at bottom, smallest disk (1) at top
            self.state = ([i for i in range(self.N, 0, -1)], [], [])

    def is_valid_move(self, move: Tuple[int, int, int]) -> bool:
        """
        Check if a move is valid for the current state of the Tower of Hanoi puzzle.

        Note: A move is valid if it can be executed from the current state. It does not
        need to result in a valid state afterwards.

        Args:
            move: A tuple (disk_id, from_peg, to_peg) where disk_id is the size of the
                 disk, and from_peg/to_peg indicate the source and destination pegs

        Returns:
            True if the move is valid, False otherwise
        """
        if not self.is_valid_state():
            return False

        try:
            disk_id, from_peg, to_peg = move

            # Check if pegs are valid indices
            if not (0 <= from_peg < 3 and 0 <= to_peg < 3):
                return False

            # Check if source and destination are different
            if from_peg == to_peg:
                return False

            # Check if source peg has any disks
            if not self.state[from_peg]:
                return False

            # Check if the disk_id matches the top disk on the source peg
            if self.state[from_peg][-1] != disk_id:
                return False

            # Check if this move is allowed (smaller disk onto larger disk or empty peg)
            if self.state[to_peg] and disk_id > self.state[to_peg][-1]:
                return False

            return True
        except Exception:
            return False

    def execute_move(self, move: Tuple[int, int, int]) -> bool:
        """
        Execute a move in the Tower of Hanoi puzzle and update the state.

        Note: It is assumed that the move starts from a valid state. A move is successful
        if the move is valid and the state after the move is valid.

        Args:
            move: A tuple (disk_id, from_peg, to_peg) for the move

        Returns:
            True if the move was successful, False otherwise
        """
        if not self.is_valid_move(move):
            return False

        try:
            disk_id, from_peg, to_peg = move

            # Convert to a mutable representation
            new_state = [list(pegs) for pegs in self.state]

            # Move the disk (we already verified it's the top disk in is_valid_move)
            disk = new_state[from_peg].pop()
            assert disk == disk_id, "Disk ID mismatch"
            new_state[to_peg].append(disk)

            # Convert back to tuple for immutability
            self.state = tuple(new_state)
            return True

        except Exception:
            return False

    def is_valid_state(self) -> bool:
        """
        Check if the current state is valid for the Tower of Hanoi.

        Returns:
            True if the state is valid, False otherwise
        """
        state = self.state
        if not isinstance(state, tuple) or len(state) != 3:
            return False

        # Check that each peg contains only disks (positive integers)
        # and that disks are in decreasing order of size from top to bottom
        # (i.e., smaller disk values represent smaller disks and must be above larger ones)
        for peg in state:
            if not all(isinstance(disk, int) and disk > 0 for disk in peg):
                return False

            # Check if disks are properly ordered (smaller disks on top of larger disks)
            for i in range(len(peg) - 1):
                if peg[i] < peg[i + 1]:
                    return False

        # Check that all disks are accounted for (1 to N)
        all_disks = sorted([disk for peg in state for disk in peg])
        expected_disks = list(range(1, self.N + 1))

        return all_disks == expected_disks

    def is_goal_reached(self) -> bool:
        """
        Check if the current state is a goal state (all disks moved to the third peg).

        Returns:
            True if all disks are on the third peg, False otherwise
        """
        if not self.is_valid_state():
            return False

        # Goal state: all disks on the third peg
        return len(self.state[2]) == self.N


class RiverCrossingSimulator(Simulator):
    """
    A simulator for the classic river crossing puzzle.

    $N$ actors and their $N$ agents want to cross a river in a boat that is capable of holding
    only $k$ people at a time, with the constraint that no actor can be in the presence
    of another agent, including while riding the boat, unless their own agent is also
    present, because each agent is worried their rivals will poach their client. Initially, all
    actors and agents are on the left side of the river with the boat. How should they cross the
    river?

    Rules:
    - Actors are represented as a_1, a_2, ... and agents with A_1, A_2, ...
    - A move is represented as a list ["A_1", "a_1"] indicating agent A_1 and actor a_1 cross the
      river together.
    - Each element in the move should be unique and represent either an actor or an agent.
    - The boat can carry only $k$ passengers at a time
    - The boat cannot go empty.
    """

    type = SimulationType.RiverCrossing

    def __init__(self, N: int, k: int = 3):
        """
        Initialize the river crossing simulator.

        Args:
            N: Number of actor-agent pairs
            k: Maximum number of passengers the boat can carry (default: 3)
        """
        self.k = k
        self.actors = [f"a_{i}" for i in range(1, N + 1)]
        self.agents = [f"A_{i}" for i in range(1, N + 1)]
        super().__init__(N)

    @property
    def params(self) -> Dict[str, Any]:
        """
        Get the parameters used to initialize this simulator.

        Returns:
            Dictionary of parameters including k
        """
        params = super().params
        params["k"] = self.k
        return params

    def reset(
        self,
        state: Optional[Union[Tuple[int, Dict[str, int]], List[Union[int, Dict[str, int]]]]] = None,
    ) -> None:
        """
        Reset the river crossing puzzle to its initial state or to a provided state.
        All actors and agents on the left bank (0), boat on left bank (0) by default.

        Args:
            state: Optional state to reset to. If None, reset to default initial state.
                  Can be either a Tuple or a List in the format (boat_position, entity_positions)

        Raises:
            ValueError: If the provided state is not valid.
        """
        if state is not None:
            old_state = self.state
            # Cast list to tuple if needed
            if isinstance(state, list):
                state = tuple(state)
            self.state = state
            if not self.is_valid_state():
                self.state = old_state
                raise ValueError("Provided state is not a valid River Crossing state.")
        else:
            # State format: (boat_position, {entity: position})
            # Position: 0 = left bank, 1 = right bank
            entity_positions = {}
            for actor in self.actors:
                entity_positions[actor] = 0
            for agent in self.agents:
                entity_positions[agent] = 0

            self.state = (0, entity_positions)  # (boat_position, entity_positions)

    def is_valid_move(self, move: List[str]) -> bool:
        """
        Check if a move is valid for the current state of the river crossing puzzle.

        Note: A move is valid if it can be executed from the current state. It does not
        need to result in a valid state afterwards.

        Args:
            move: List of actors and/or agents to move across the river

        Returns:
            True if the move is valid, False otherwise
        """
        if not self.is_valid_state():
            return False

        try:
            boat_position, entity_positions = self.state

            # Check if the move is a valid list
            if not isinstance(move, list) or not move:
                return False

            # Check passenger count constraint
            if len(move) > self.k:
                return False

            # Check if all passengers are valid entities
            all_entities = self.actors + self.agents
            if not all(passenger in all_entities for passenger in move):
                return False

            # Check for duplicates in the move
            if len(move) != len(set(move)):
                return False

            # Check if all passengers are at the same side as the boat
            if not all(entity_positions[passenger] == boat_position for passenger in move):
                return False

            return True

        except Exception:
            return False

    def execute_move(self, move: List[str]) -> bool:
        """
        Execute a move in the river crossing puzzle and update the state.

        Note: It is assumed that the move starts from a valid state. A move is successful
        if the move is valid and the state after the move is valid.

        Args:
            move: List of actors and/or agents to move across the river

        Returns:
            True if the move was successful, False otherwise
        """
        if not self.is_valid_move(move):
            return False

        try:
            boat_position, entity_positions = self.state

            # Calculate new positions after the move
            new_boat_position = 1 - boat_position
            new_entity_positions = entity_positions.copy()
            for passenger in move:
                new_entity_positions[passenger] = new_boat_position

            # Create the new state
            new_state = (new_boat_position, new_entity_positions)

            # Check if the new state would be valid
            temp_simulator = RiverCrossingSimulator(self.N, self.k)
            temp_simulator.state = new_state
            if not temp_simulator.is_valid_state():
                return False

            # Update state
            self.state = new_state
            return True

        except Exception:
            return False

    def is_valid_state(self) -> bool:
        """
        Check if the current state is valid for the river crossing puzzle.

        Returns:
            True if the state is valid, False otherwise
        """
        try:
            boat_position, entity_positions = self.state

            # Check boat position is valid
            if boat_position not in (0, 1):
                return False

            # Check all entities are accounted for
            all_entities = self.actors + self.agents
            if set(entity_positions.keys()) != set(all_entities):
                return False

            # Check all positions are valid
            if not all(pos in (0, 1) for pos in entity_positions.values()):
                return False

            # Check the constraint: no actor can be with another agent unless their own agent is present
            for i, actor in enumerate(self.actors):
                actor_agent = self.agents[i]  # corresponding agent
                actor_pos = entity_positions[actor]

                # Check each agent that is at the same location as the actor
                for j, agent in enumerate(self.agents):
                    if i == j:  # Skip actor's own agent
                        continue

                    if entity_positions[agent] == actor_pos:
                        # Another agent is present with this actor
                        if entity_positions[actor_agent] != actor_pos:
                            return False  # Actor's own agent must also be present
        except Exception:
            return False
        return True

    def is_goal_reached(self) -> bool:
        """
        Check if the current state is the goal state (all entities on the right bank).

        Returns:
            True if all entities are on the right bank, False otherwise
        """
        try:
            _, entity_positions = self.state
            return all(position == 1 for position in entity_positions.values())
        except Exception:
            return False


def create_simulator(simulator_type: SimulationType, params: Dict[str, Any]) -> Simulator:
    """
    Factory function to create a simulator of the specified type with the given parameters.

    Args:
        simulator_type: Type of simulator to create (SimulationType enum)
        params: Dictionary of parameters for the simulator

    Returns:
        An instance of the specified simulator

    Raises:
        ValueError: If the simulator type is unknown
    """
    if simulator_type == SimulationType.TowerOfHanoi:
        return TowerOfHanoiSimulator(N=params["N"])
    elif simulator_type == SimulationType.RiverCrossing:
        return RiverCrossingSimulator(N=params["N"], k=params.get("k", 3))
    else:
        raise ValueError(f"Unknown simulator type: {simulator_type}")
