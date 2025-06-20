import numpy as np
import matplotlib.pyplot as plt
import json
import gymnasium as gym
import time
import sys
import os
from envs.ui.sprites import load_srpite_map

from envs.constants import config, Action
from envs.grid import Grid
from envs.ui.training_room import TrainingRoom



LEARN = True
N_EPISODES = 1000

load_srpite_map()


gym.envs.registration.register(
    id="FireFighterWorld-v0",  # It's good practice to add a version
    entry_point="envs:FireFighterWorld",
)


class FireEvacuationAgentMDP:
    def __init__(self, seed=None):
        self.np_random = np.random.RandomState(seed)
        self.grid_template = Grid(
            TrainingRoom(),
            static_mode=True,
            initial_agent_pos=np.array([0, 0]),
            initial_target_pos=np.array([0, 0]),
            np_random=self.np_random,
        )
        self.rows = config.grid_size
        self.cols = config.grid_size
        self.actions = [
            Action.UP,
            Action.DOWN,
            Action.LEFT,
            Action.RIGHT,
            Action.PUT_OUT_FIRE,
        ]
        self.movement_actions = [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT]
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
        self.P = self._build_transition_probabilities()
        self.R = self._build_reward_function()
        self.value_function = np.zeros(self.num_states)
        self.policy = np.zeros(self.num_states, dtype=int)
        print(f"MDP Initialized with {self.num_states} states and {len(self.actions)} actions.")
        print("Starting Value Iteration...")
        self.value_iteration(epsilon=1e-6)
        print("Value Iteration complete. Optimal policy computed.")

    def _define_states(self) -> list[tuple]:
        states = []
        for ax, ay in self.possible_traversable_positions:
            for tx, ty in self.possible_traversable_positions:
                states.append((ax, ay, tx, ty))
        return states

    def _build_transition_probabilities(self) -> np.ndarray:
        P = np.zeros((self.num_states, len(self.actions), self.num_states))
        env_simulator = gym.make("FireFighterWorld", render_mode=None, static_mode=True)
        slip_prob = 0.2

        for s_idx, (ax, ay, tx, ty) in enumerate(self.states):
            preset_fire_positions = [(5, 0), (5, 1), (5, 3)]
            observation, info = env_simulator.reset(
                options={
                    "initial_agent_pos": np.array([ax, ay]),
                    "initial_target_pos": np.array([tx, ty]),
                    "preset_fire_mode": True,
                    "preset_fire_positions": preset_fire_positions,
                }
            )

            current_agent_pos = np.array(observation[0])
            current_target_pos = np.array(observation[1])

            for a_idx, action in enumerate(self.actions):
                preset_fire_positions = [(5, 0), (5, 1), (5, 3)]
                observation, info = env_simulator.reset(
                    options={
                        "initial_agent_pos": np.array([ax, ay]),
                        "initial_target_pos": np.array([tx, ty]),
                        "preset_fire_mode": True,
                        "preset_fire_positions": preset_fire_positions,
                    }
                )
                next_observation, reward, terminated, truncated, next_info = env_simulator.step(action.value)
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
                    P[s_idx, a_idx, s_idx] = 1.0
                    print(
                        f"Warning: Calculated next state {next_s_tuple} not in defined state space."
                    )
        env_simulator.close()
        return P

    def _build_reward_function(self) -> np.ndarray:
        R = np.zeros((self.num_states, len(self.actions)))
        env_simulator = gym.make("FireFighterWorld", render_mode=None, static_mode=True)

        for s_idx, (ax, ay, tx, ty) in enumerate(self.states):
            current_agent_pos = np.array([ax, ay])
            current_target_pos = np.array([tx, ty])

            for a_idx, action in enumerate(self.actions):
                preset_fire_positions = [(5, 0), (5, 1), (5, 3)]
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
        V = np.copy(self.value_function)
        gamma = config.discount_factor
        iteration = 0
        while True:
            iteration += 1
            V_new = np.zeros(self.num_states)
            delta = 0

            for s_idx in range(self.num_states):
                q_values = np.zeros(len(self.actions))
                for a_idx in range(len(self.actions)):
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

        # The MDP policy is deterministic, so the epsilon-greedy part should be handled here
        # or removed if you always want the optimal action.
        # For evaluation of the MDP, we typically want to always follow the optimal policy.
        # If you want to introduce some stochasticity for robustness testing, keep the if.
        # Otherwise, remove the if/else and just return the optimal action.
        if np.random.uniform(0, 1) < 1.0: # Always follow optimal policy for evaluation
            s_idx = self.state_to_idx[current_state_tuple]
            optimal_action_idx = self.policy[s_idx]
            return self.actions[optimal_action_idx]
        else:
            return np.random.choice(self.actions) # This part is typically not used for MDP evaluation

    def get_value_function(self):
        return self.value_function

    def get_policy(self):
        return self.policy

    def __str__(self) -> str:
        return "FireEvacuationAgentMDP (Solver Ready)"


sys.path.insert(0, os.path.abspath("."))


# Ensure your constants are set up for a static environment for MDP
config.chance_of_catching_fire = 0
config.chance_of_self_extinguish = 0
config.static_fire_mode = True

print(f"Running in static fire mode: {config.static_fire_mode}")
print(f"Grid size: {config.grid_size}")
print(f"Reward for success: {config.evacuation_success_reward}")
print(f"Discount factor: {config.discount_factor}")


LEARN = True
N_EPISODES = 1000

load_srpite_map()

class Metrics:
    def __init__(self):
        self.episodes_data = []
        self.current_cluster = []
        self.cluster_size = max(1, N_EPISODES // 100)

    def log_episode(self, total_reward, steps, illegal_moves, deaths, initial_distance):
        ratio = initial_distance / steps if steps > 0 else 0
        self.current_cluster.append({
            "reward": total_reward,
            "illegal_moves": illegal_moves,
            "deaths": deaths,
            "steps_to_distance": ratio
        })
        if len(self.current_cluster) >= self.cluster_size:
            self.aggregate_cluster()

    def aggregate_cluster(self):
        cluster = self.current_cluster
        agg = {
            "reward": np.mean([ep["reward"] for ep in cluster]),
            "illegal_moves": np.mean([ep["illegal_moves"] for ep in cluster]),
            "deaths": np.mean([ep["deaths"] for ep in cluster]),
            "steps_to_distance": np.mean([ep["steps_to_distance"] for ep in cluster])
        }
        self.episodes_data.append(agg)
        self.current_cluster = []

    def save_plots(self):
        if not LEARN or not self.episodes_data:
            print("No metrics to save or LEARN=False")
            return

        x = range(len(self.episodes_data))
        fig, axs = plt.subplots(2, 2, figsize=(14, 10))
        fig.suptitle("MDP Simulation Metrics Per Episode Cluster", fontsize=16)

        def plot_metric(ax, key, title, ylabel, color):
            ax.plot(x, [d[key] for d in self.episodes_data], label=key, color=color, alpha=0.6)
            ax.set_title(title)
            ax.set_xlabel("Episode Cluster")
            ax.set_ylabel(ylabel)
            ax.grid(True)
            ax.legend()

        plot_metric(axs[0, 0], "reward", "Average Total Reward", "Reward", "blue")
        plot_metric(axs[0, 1], "illegal_moves", "Average Illegal Moves", "Illegal Moves", "red")
        plot_metric(axs[1, 0], "deaths", "Average Deaths", "Deaths", "black")
        plot_metric(axs[1, 1], "steps_to_distance", "Efficiency (Steps/Distance)", "Ratio", "purple")

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        os.makedirs("metrics", exist_ok=True)
        plt.savefig(f"metrics/mdp_metrics.dr={config.distance_reward}.tsp={config.time_step_punishment}.N={N_EPISODES}.png")
        plt.close()


gym.envs.registration.register(
    id="FireFighterWorld-v0",
    entry_point="envs:FireFighterWorld",
)


config.chance_of_catching_fire = 0
config.chance_of_self_extinguish = 0
config.static_fire_mode = True


def run_mdp_simulation_with_metrics(num_episodes=N_EPISODES):
    mdp_solver = FireEvacuationAgentMDP(seed=42)
    env = gym.make("FireFighterWorld-v0", render_mode="human", static_mode=True)
    metrics = Metrics()

    preset_fire_positions = [(5, 0), (5, 1), (5, 3)]
    for episode in range(num_episodes):
        initial_agent_pos = np.array([0, 5])
        initial_target_pos = np.array([0, 0])
        obs, _ = env.reset(options={
            "initial_agent_pos": initial_agent_pos,
            "initial_target_pos": initial_target_pos,
            "preset_fire_mode": True,
            "preset_fire_positions": preset_fire_positions,
        })

        agent_pos = obs[0]
        target_pos = obs[1]
        total_reward, illegal_moves, deaths, steps = 0, 0, 0, 0
        max_steps = 100

        initial_distance = np.linalg.norm(initial_agent_pos - initial_target_pos)
        if initial_distance == 0:
            initial_distance = 1

        done = False
        while not done and steps < max_steps:
            action = mdp_solver.get_optimal_action(agent_pos, target_pos)
            next_obs, reward, terminated, truncated, _ = env.step(action.value)

            legal = True
            if reward < config.time_step_punishment and np.array_equal(next_obs[0], agent_pos):
                legal = False
                illegal_moves += 1

            total_reward += reward
            agent_pos = next_obs[0]
            target_pos = next_obs[1]
            steps += 1
            done = terminated or truncated
            env.render()
            time.sleep(0.05)

        metrics.log_episode(total_reward, steps, illegal_moves, deaths, initial_distance)

    metrics.save_plots()
    env.close()



if __name__ == "__main__":
    try:
        os.makedirs("metrics", exist_ok=True)
        run_mdp_simulation_with_metrics(num_episodes=5)
    except KeyboardInterrupt:
        print("MDP simulation interrupted.")
    finally:
        plt.close('all')