import gymnasium as gym
import numpy as np
import time  # Import time for sleep
import sys
import os
from mdp.agent import FireEvacuationAgentMDP
from envs.ui.sprites import load_srpite_map

load_srpite_map()

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
    # The MDP solver's internal `gym.make` calls will now find 'FireFighterWorld-v0'
    mdp_solver = FireEvacuationAgentMDP(seed=42)

    print("Creating environment for visualization...")
    # Create the environment in static mode for visualization
    env = gym.make("FireFighterWorld-v0", render_mode="human", static_mode=True)

    # Define an initial state for the simulation (e.g., agent at (0,0), target at (3,2))
    # Make sure these positions are traversable in your grid setup.
    # Note: Your Grid's `create_grid` will use these if `static_mode=True`.
    initial_agent_pos = np.array([0, 5])
    initial_target_pos = np.array(
        [0, 0]
    )  # Example, adjust as needed based on your walls/traversable tiles

    print(
        f"Resetting environment to initial state: Agent at {initial_agent_pos}, Target at {initial_target_pos}"
    )
    # Reset the environment to the specific initial state
    observation, info = env.reset(
        options={
            "initial_agent_pos": initial_agent_pos,
            "initial_target_pos": initial_target_pos,
        }
    )

    # The observation from env.reset will be the agent's (x,y) if your _get_obs() is still like that.
    # We need to explicitly get target_pos from info.
    agent_current_pos = observation[0]
    target_current_pos = np.array(info["target_pos"])  # Get target pos from info dict

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
        # Ensure that `current_agent_pos` and `current_target_pos` are tuples for `get_optimal_action`
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
        target_current_pos = np.array(
            next_info["target_pos"]
        )  # Target position is static

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
