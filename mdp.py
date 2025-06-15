import gymnasium as gym
import numpy as np
import time  # Import time for sleep
import sys
import os
from envs.ui.sprites import load_srpite_map

load_srpite_map()


import numpy as np
from enum import Enum  # Needed for Action enum
from envs.constants import Config, Action  # Import config and Action enum
from envs.grid import Grid  # To instantiate a template grid for map info
import gymnasium as gym  # Import gymnasium to use your env in MDP
from envs.ui.training_room import TrainingRoom
from envs.constants import config

# Define constants if not already imported or globally accessible
# (though it's better to get them from config)
# GRID_SIZE = config.grid_size # Example


class FireEvacuationAgentMDP:
    def __init__(self, seed=None):
        """
        Initializes the FireEvacuationAgentMDP (the MDP solver).
        This class pre-computes the optimal policy for a STATIC fire environment.
        """
        self.np_random = np.random.RandomState(seed)

        # Create a template grid instance to read map information (walls, static fire positions)
        # This grid instance should *not* be used for live simulation steps.
        # It's specifically for the MDP solver to build its P and R matrices.
        # Pass static_mode=True to ensure the grid is initialized predictably.
        # We also pass dummy initial positions here, they'll be overwritten when iterating states.
        self.grid_template = Grid(
            TrainingRoom(),
            static_mode=True,
            initial_agent_pos=np.array([0, 0]),  # Dummy
            initial_target_pos=np.array([0, 0]),
            np_random=self.np_random,
        )  # Dummy

        self.rows = config.grid_size
        self.cols = config.grid_size

        # Define the set of actions the MDP can take
        self.actions = [
            Action.UP,
            Action.DOWN,
            Action.LEFT,
            Action.RIGHT,
            Action.PUT_OUT_FIRE,  # Include put out fire as an action
        ]
        self.movement_actions = [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT]

        # Determine all possible agent and target positions based on traversable tiles
        self.possible_traversable_positions = []
        for y in range(self.rows):
            for x in range(self.cols):
                if (
                    self.grid_template.tiles[x][y]
                    and self.grid_template.tiles[x][y].is_traversable
                ):
                    self.possible_traversable_positions.append((x, y))

        # 1. Define All Possible States
        # State: (agent_x, agent_y, target_x, target_y)
        self.states = self._define_states()
        self.num_states = len(self.states)
        self.state_to_idx = {state: i for i, state in enumerate(self.states)}
        self.idx_to_state = {i: state for i, state in enumerate(self.states)}

        # 2. Build Transition Probabilities (P) and Reward Function (R)
        self.P = self._build_transition_probabilities()  # P[s_idx, a_idx, s_prime_idx]
        self.R = self._build_reward_function()  # R[s_idx, a_idx]

        # 3. Initialize Value Function and Policy
        self.value_function = np.zeros(self.num_states)
        self.policy = np.zeros(
            self.num_states, dtype=int
        )  # Stores index of optimal action

        print(
            f"MDP Initialized with {self.num_states} states and {len(self.actions)} actions."
        )
        print("Starting Value Iteration...")
        # 4. Run Value Iteration to compute the optimal policy
        self.value_iteration(epsilon=1e-6)  # Using a small epsilon for convergence
        print("Value Iteration complete. Optimal policy computed.")

    def _define_states(self) -> list[tuple]:
        """
        Defines the state space as (agent_x, agent_y, target_x, target_y).
        Only includes positions that are traversable.
        """
        states = []
        for ax, ay in self.possible_traversable_positions:
            for tx, ty in self.possible_traversable_positions:
                states.append((ax, ay, tx, ty))
        return states

    def _build_transition_probabilities(self) -> np.ndarray:
        """
        Builds the transition probability matrix P[s_idx, a_idx, s_prime_idx].
        Since fire is static and moves are deterministic (if legal),
        P will mostly contain 1.0 for the expected next state and 0.0 otherwise.
        """
        P = np.zeros((self.num_states, len(self.actions), self.num_states))

        # Temporarily create a FireFighterWorld instance in static mode
        # to simulate transitions for the MDP.
        # This allows us to use the same step logic as the environment.
        # We will reset this environment for each state to simulate transitions.
        # Use render_mode=None as we don't need rendering for building P and R.
        env_simulator = gym.make("FireFighterWorld", render_mode=None, static_mode=True)
        slip_prob = 0.2

        
        for s_idx, (ax, ay, tx, ty) in enumerate(self.states):
            # Reset the simulator environment to the current state (ax, ay, tx, ty)
            # using the options parameter for initial positions.
            preset_fire_positions = [(5, 0), (5,1), (5,3)]

            observation, info = env_simulator.reset(
                options={
                    "initial_agent_pos": np.array([ax, ay]),
                    "initial_target_pos": np.array([tx, ty]),
                    "preset_fire_mode": True,
                    "preset_fire_positions": preset_fire_positions,
                }
            )


            # Get the actual positions from the reset grid to ensure consistency
            # (though with static_mode and initial_pos, it should match)
            current_agent_pos = np.array(observation[0])  # if you only care about the agent
            current_target_pos = np.array(observation[1])


            for a_idx, action in enumerate(self.actions):
                # Simulate the step using the environment's logic
                # Need to reset the environment to the *current* state before each action simulation
                # because env_simulator.step changes its internal state.
                preset_fire_positions = [(5, 0), (5,1), (5,3)]

                observation, info = env_simulator.reset(
                    options={
                        "initial_agent_pos": np.array([ax, ay]),
                        "initial_target_pos": np.array([tx, ty]),
                        "preset_fire_mode": True,
                        "preset_fire_positions": preset_fire_positions,
                    }
                )


                next_observation, reward, terminated, truncated, next_info = (
                    env_simulator.step(action.value)
                )
                next_agent_pos = next_observation[0]
                next_target_pos = next_observation[1]

                next_s_tuple = (
                    next_agent_pos[0],
                    next_agent_pos[1],
                    next_target_pos[0],
                    next_target_pos[1],
                )

                if next_s_tuple in self.state_to_idx:
                    next_s_idx = self.state_to_idx[next_s_tuple]
                    P[s_idx, a_idx, next_s_idx] = 1.0
                else:
                    # This case indicates an error in state definition or transition logic
                    # For safety, make it transition to current state if somehow invalid.
                    P[s_idx, a_idx, s_idx] = 1.0
                    print(
                        f"Warning: Calculated next state {next_s_tuple} not in defined state space."
                    )

        env_simulator.close()  # Close the simulator environment
        return P

    def _build_reward_function(self) -> np.ndarray:
        """
        Builds the reward function R[s_idx, a_idx].
        Rewards are associated with taking an action from a state.
        """
        R = np.zeros((self.num_states, len(self.actions)))

        # Temporarily create a FireFighterWorld instance in static mode
        env_simulator = gym.make("FireFighterWorld", render_mode=None, static_mode=True)

        for s_idx, (ax, ay, tx, ty) in enumerate(self.states):
            current_agent_pos = np.array([ax, ay])
            current_target_pos = np.array([tx, ty])

            for a_idx, action in enumerate(self.actions):
                # Reset the simulator environment to the current state (ax, ay, tx, ty)
                preset_fire_positions = [(5, 0), (5,1), (5,3)]  # Example: fire at (3,2) as you want

                observation, info = env_simulator.reset(
                    options={
                        "initial_agent_pos": np.array([ax, ay]),
                        "initial_target_pos": np.array([tx, ty]),
                        "preset_fire_mode": True,
                        "preset_fire_positions": preset_fire_positions,
                    }
                )


                # Take the step to get the reward
                _, reward, _, _, _ = env_simulator.step(action.value)
                R[s_idx, a_idx] = reward

        env_simulator.close()  # Close the simulator environment
        return R

    def value_iteration(self, epsilon=1e-6):
        """
        Performs Value Iteration to find the optimal value function and policy.
        """
        V = np.copy(self.value_function)
        gamma = config.discount_factor  # Get discount factor from config

        iteration = 0
        while True:
            iteration += 1
            V_new = np.zeros(self.num_states)
            delta = 0

            for s_idx in range(self.num_states):
                q_values = np.zeros(len(self.actions))
                for a_idx in range(len(self.actions)):
                    # Calculate expected future reward based on P and V
                    expected_future_reward = np.sum(self.P[s_idx, a_idx, :] * V)

                    q_values[a_idx] = (
                        self.R[s_idx, a_idx] + gamma * expected_future_reward
                    )

                # If a state has no valid actions leading anywhere (e.g., surrounded by walls/fire,
                # and no valid moves/actions, though unlikely with current setup), handle this:
                if q_values.size > 0:
                    V_new[s_idx] = np.max(q_values)
                    self.policy[s_idx] = np.argmax(q_values)
                else:
                    # Fallback for states with no meaningful Q-values (should ideally not happen)
                    V_new[s_idx] = 0  # Or some large negative value
                    self.policy[s_idx] = 0  # Default to first action (e.g., UP)

                delta = max(delta, abs(V_new[s_idx] - V[s_idx]))

            V = V_new
            if delta < epsilon:
                print(f"Value Iteration converged in {iteration} iterations.")
                break
            if iteration % 100 == 0:
                print(f"Value Iteration: {iteration} iterations, Delta: {delta:.6f}")

        self.value_function = V
        return self.policy, self.value_function

    def get_optimal_action(
        self, current_agent_pos: np.ndarray, current_target_pos: np.ndarray
    ) -> Action:
        """
        Given the current agent and target positions, returns the optimal action
        from the pre-computed policy.
        """
        current_state_tuple = (
            current_agent_pos[0],
            current_agent_pos[1],
            current_target_pos[0],
            current_target_pos[1],
        )

        if current_state_tuple not in self.state_to_idx:
            # This should ideally not happen if your environment only generates states
            # that are part of your defined state space.
            print(
                f"Error: Current state {current_state_tuple} not found in MDP state space. Returning default action."
            )
            return Action.UP  # Fallback to a default action

        if np.random.uniform(0, 1) < .8:
            s_idx = self.state_to_idx[current_state_tuple]
            optimal_action_idx = self.policy[s_idx]
            return self.actions[optimal_action_idx]  # Return the actual Action enum member
        else:
            return np.random.choice(self.actions)

    def get_value_function(self):
        return self.value_function

    def get_policy(self):
        return self.policy

    def __str__(self) -> str:
        return "FireEvacuationAgentMDP (Solver Ready)"

# Add the directory containing your 'envs' package to the Python path
# Adjust this path if your notebook is not in the same directory as 'envs'
sys.path.insert(0, os.path.abspath(".."))

# Import your config and Action enum
from envs.constants import config, Action

# Import your FireFighterWorld environment class
from envs.grid_world import FireFighterWorld

gym.envs.registration.register(
    id="FireFighterWorld-v0",  # It's good practice to add a version
    entry_point="envs:FireFighterWorld",
    # You might want to specify max_episode_steps here, e.g., if you have a time limit for the MDP
    # max_episode_steps=100,
    # Or keep it out if your loop handles truncation.
)


# Ensure your constants are set up for a static environment for MDP
config.chance_of_catching_fire = 0  # Ensure no new fire appears
config.chance_of_self_extinguish = 0  # Ensure existing fire doesn't extinguish randomly

# Set static_fire_mode in config BEFORE initializing MDP solver or environment
# This flag affects how Grid initializes (e.g., character placement based on mode)
config.static_fire_mode = True

print(f"Running in static fire mode: {config.static_fire_mode}")
print(f"Grid size: {config.grid_size}")
print(f"Reward for success: {config.evacuation_success_reward}")
print(f"Discount factor: {config.discount_factor}")


def run_mdp_simulation():
    print("Initializing MDP Solver...")
    # Initialize the MDP solver (this will compute the policy)
    # The MDP solver's internal gym.make calls will now find 'FireFighterWorld-v0'
    mdp_solver = FireEvacuationAgentMDP(seed=42)

    print("Creating environment for visualization...")
    # Create the environment in static mode for visualization
    env = gym.make("FireFighterWorld-v0", render_mode="human", static_mode=True)

    # Define an initial state for the simulation (e.g., agent at (0,0), target at (3,2))
    # Make sure these positions are traversable in your grid setup.
    # Note: Your Grid's create_grid will use these if static_mode=True.
    initial_agent_pos = np.array([0, 5])
    initial_target_pos = np.array(
        [0, 0]
    )  # Example, adjust as needed based on your walls/traversable tiles

    print(
        f"Resetting environment to initial state: Agent at {initial_agent_pos}, Target at {initial_target_pos}"
    )
    
    preset_fire_positions = [(5, 0), (5,1), (5,3)]  # Example: fire at (3,2) as you want

    observation, info = env.reset(
        options={
            "initial_agent_pos": initial_agent_pos,
            "initial_target_pos": initial_target_pos,
            "preset_fire_mode": True,
            "preset_fire_positions": preset_fire_positions,
        }
    )

    # The observation from env.reset will be the agent's (x,y) if your _get_obs() is still like that.
    # We need to explicitly get target_pos from info.
    agent_current_pos = observation[0]
    target_current_pos = observation[1]  # Get target pos from info dict

    print(
        f"Starting MDP simulation from Agent: {agent_current_pos}, Target: {target_current_pos}"
    )

    done = False
    total_reward = 0
    step_count = 0
    max_simulation_steps = 100  # Add a hard step limit to prevent infinite loops

    while not done and step_count < max_simulation_steps:
        step_count += 1

        # Get the optimal action from the pre-computed MDP policy
        # Ensure that current_agent_pos and current_target_pos are tuples for get_optimal_action
        optimal_action = mdp_solver.get_optimal_action(
            agent_current_pos, target_current_pos
        )

        print(
            f"Step {step_count}: Agent at {agent_current_pos}, Target at {target_current_pos}. Optimal Action: {optimal_action.name}"
        )



        # Take the optimal action in the environment.
        # Ensure you are passing the Action enum value (integer) to env.step()
        next_observation, reward, terminated, truncated, next_info = env.step(
            optimal_action.value
        )

        # Update current positions from the environment's step output
        agent_current_pos = next_observation[0]
        target_current_pos = next_observation[1]

        total_reward += reward
        done = terminated or truncated

        # Render the frame to show the action
        env.render()
        time.sleep(0.5)  # Slow down rendering for better visualization

    print(f"Simulation finished in {step_count} steps. Total Reward: {total_reward}")
    env.close()


if __name__ == "__main__":
    try:
        run_mdp_simulation()
    except KeyboardInterrupt:
        print("MDP simulation interrupted.")
        pass
