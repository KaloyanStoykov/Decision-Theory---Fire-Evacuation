import gymnasium as gym
import numpy as np
import time  # Import time for sleep
import sys
import os
from envs.ui.sprites import load_srpite_map

load_srpite_map()


import numpy as np
from enum import Enum
from envs.constants import Config, Action
from envs.grid import Grid
import gymnasium as gym
from envs.ui.training_room import TrainingRoom
from envs.constants import config

from envs.grid_world import FireFighterWorld



class FireEvacuationAgentMDP:
    def __init__(self, seed=None):
        """
        Initializes the FireEvacuationAgentMDP (the MDP solver).
        This class pre-computes the optimal policy for a STATIC fire environment.
        """
        self.np_random = np.random.RandomState(seed)


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
        self.value_iteration(epsilon=1e-6)
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


            current_agent_pos = np.array(observation[0])  # if you only care about the agent
            current_target_pos = np.array(observation[1])


            for a_idx, action in enumerate(self.actions):
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
                    # For safety, make it transition to current state if somehow invalid.
                    P[s_idx, a_idx, s_idx] = 1.0
                    print(
                        f"Warning: Calculated next state {next_s_tuple} not in defined state space."
                    )

        env_simulator.close()
        return P

    def _build_reward_function(self) -> np.ndarray:
        """
        Builds the reward function R[s_idx, a_idx].
        Rewards are associated with taking an action from a state.
        """
        R = np.zeros((self.num_states, len(self.actions)))

        env_simulator = gym.make("FireFighterWorld", render_mode=None, static_mode=True)

        for s_idx, (ax, ay, tx, ty) in enumerate(self.states):
            current_agent_pos = np.array([ax, ay])
            current_target_pos = np.array([tx, ty])

            for a_idx, action in enumerate(self.actions):
                preset_fire_positions = [(5, 0), (5,1), (5,3)]

                observation, info = env_simulator.reset(
                    options={
                        "initial_agent_pos": np.array([ax, ay]),
                        "initial_target_pos": np.array([tx, ty]),
                        "preset_fire_mode": True,
                        "preset_fire_positions": preset_fire_positions,
                    }
                )


                _, reward, _, _, _ = env_simulator.step(action.value)
                R[s_idx, a_idx] = reward

        env_simulator.close()
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

                if q_values.size > 0:
                    V_new[s_idx] = np.max(q_values)
                    self.policy[s_idx] = np.argmax(q_values)
                else:
                    V_new[s_idx] = 0  
                    self.policy[s_idx] = 0

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
            print(
                f"Error: Current state {current_state_tuple} not found in MDP state space. Returning default action."
            )
            return Action.UP

        if np.random.uniform(0, 1) < .8:
            s_idx = self.state_to_idx[current_state_tuple]
            optimal_action_idx = self.policy[s_idx]
            return self.actions[optimal_action_idx]
        else:
            return np.random.choice(self.actions)

    def get_value_function(self):
        return self.value_function

    def get_policy(self):
        return self.policy

    def __str__(self) -> str:
        return "FireEvacuationAgentMDP (Solver Ready)"

sys.path.insert(0, os.path.abspath(".."))



gym.envs.registration.register(
    id="FireFighterWorld-v0",
    entry_point="envs:FireFighterWorld",
)


# Static environment vars
config.chance_of_catching_fire = 0
config.chance_of_self_extinguish = 0

config.static_fire_mode = True

print(f"Running in static fire mode: {config.static_fire_mode}")
print(f"Grid size: {config.grid_size}")
print(f"Reward for success: {config.evacuation_success_reward}")
print(f"Discount factor: {config.discount_factor}")


def run_mdp_simulation():
    print("Initializing MDP Solver...")
    mdp_solver = FireEvacuationAgentMDP(seed=42)

    print("Creating environment for visualization...")
    env = gym.make("FireFighterWorld-v0", render_mode="human", static_mode=True)

   
    initial_agent_pos = np.array([0, 5])
    initial_target_pos = np.array(
        [0, 0]
    ) 

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
        optimal_action = mdp_solver.get_optimal_action(
            agent_current_pos, target_current_pos
        )

        print(
            f"Step {step_count}: Agent at {agent_current_pos}, Target at {target_current_pos}. Optimal Action: {optimal_action.name}"
        )



        
        next_observation, reward, terminated, truncated, next_info = env.step(
            optimal_action.value
        )

        agent_current_pos = next_observation[0]
        target_current_pos = next_observation[1]

        total_reward += reward
        done = terminated or truncated

        # Render the frame to show the action
        env.render()
        time.sleep(0.5)

    print(f"Simulation finished in {step_count} steps. Total Reward: {total_reward}")
    env.close()


if __name__ == "__main__":
    try:
        run_mdp_simulation()
    except KeyboardInterrupt:
        print("MDP simulation interrupted.")
        pass
