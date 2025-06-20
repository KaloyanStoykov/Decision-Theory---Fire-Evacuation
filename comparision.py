import matplotlib.pyplot as plt
import gymnasium as gym
import numpy as np
from q_learning.agent import Agent
from q_learning.constants import RENDER, MAX_STEPS_PER_EPISODE
from envs.constants import config
from envs.ui.sprites import load_srpite_map
from mdp import FireEvacuationAgentMDP


def create_env():
    gym.envs.registration.register(
        id="FireFighterWorld",
        entry_point="envs:FireFighterWorld",
    )

    env = gym.make("FireFighterWorld", render_mode="human" if RENDER else "rgb_array")
    env.reset(seed=42, options={"preset_fire_positions": [(3, 2)]})

    return env


class Metrics:
    rewards = 0
    illegal_moves = 0
    steps = 0
    is_successful = False
    episodes = []

    def save(self):
        self.episodes.append(
            {
                "steps": self.steps,
                "rewards": self.rewards,
                "illegal_moves": self.illegal_moves,
                "is_successful": self.is_successful,
            }
        )
        self.clear()

    def clear(self):
        self.rewards = 0
        self.steps = 0
        self.illegal_moves = 0
        self.is_successful = False


config.static_fire_mode = True
# config.random_target_location = False

load_srpite_map()


preset_fire_positions = [
    (5, 0),
    (5, 1),
    (5, 3),
]

unavailable = [
    (0, 2),
    (1, 2),
    (1, 3),
    (2, 3),
    (3, 3),
    (3, 0),
    (3, 1),
    (0, 3),
    (1, 0),
    (2, 0),
]

unavailable += preset_fire_positions

q_learning_agent = Agent(seed=42)
q_metrics = Metrics()
mdp_agent = FireEvacuationAgentMDP(seed=42)
mdp_metrics = Metrics()


def test_q(env, target_pos, agent_pos):
    observation, info = env.reset(
        options={
            "initial_agent_pos": agent_pos,
            "initial_target_pos": target_pos,
            "preset_fire_mode": True,
            "preset_fire_positions": preset_fire_positions,
        }
    )

    for _ in range(MAX_STEPS_PER_EPISODE):
        action = q_learning_agent.get_action(env.action_space, observation)

        next_observation, reward, terminated, _, info = env.step(action)

        q_metrics.steps += 1
        q_metrics.rewards += reward
        q_metrics.illegal_moves = info["is_legal_move"]
        q_metrics.is_successful = not info["is_agent_dead"]

        q_learning_agent.update(
            observation, action, reward, terminated, next_observation
        )
        observation = next_observation

        if terminated:
            break

    q_metrics.save()


def test_mdp(env, target_pos, agent_pos):
    agent_current_pos = agent_pos
    target_current_pos = target_pos

    env.reset(
        options={
            "initial_agent_pos": agent_pos,
            "initial_target_pos": target_pos,
            "preset_fire_mode": True,
            "preset_fire_positions": preset_fire_positions,
        }
    )

    while not done and step_count < MAX_STEPS_PER_EPISODE:
        step_count += 1

        # Get the optimal action from the pre-computed MDP policy
        optimal_action = mdp_agent.get_optimal_action(
            agent_current_pos, target_current_pos
        )

        next_observation, reward, terminated, truncated, next_info = env.step(
            optimal_action.value
        )

        q_metrics.steps += 1
        q_metrics.rewards += reward
        q_metrics.illegal_moves = next_info["is_legal_move"]
        q_metrics.is_successful = not next_info["is_agent_dead"]

        agent_current_pos = next_observation[0]
        target_current_pos = next_observation[1]

        done = terminated or truncated

        if done:
            break

    mdp_metrics.save()


def show():
    ep_nr = range(len(q_metrics.episodes))
    fig, axs = plt.subplots(1, 1, figsize=(10, 10))

    axs[0, 0].plot(
        ep_nr,
        [episode["reward"] for episode in self.episodes],
        label="Reward",
        alpha=0.6,
    )
    axs[0, 0].set_title("Total Reward per Episode")
    axs[0, 0].set_xlabel("Episode")
    axs[0, 0].set_ylabel("Reward")

    plt.legend()
    plt.savefig(f"metrics/comparison.png")
    plt.close()


def run():
    env = create_env()
    observation, _ = env.reset(options={"preset_fire_positions": preset_fire_positions})

    for ax in range(config.grid_size):
        for ay in range(config.grid_size):
            if any((ax, ay) == pos for pos in unavailable):
                continue

            for tx in range(config.grid_size):
                for ty in range(config.grid_size):
                    if (tx == ax and ty == ay) or any(
                        (tx, ty) == pos for pos in unavailable
                    ):
                        continue

                    test_mdp((tx, ty), (ax, ay))
                    test_q((tx, ty), (ax, ay))

    env.close()
    show()


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:

        pass
