import numpy as np
import matplotlib.pyplot as plt
from q_learning.constants import LEARN, N_EPISODES
import json
from envs.constants import config


class Metrics:
    def __init__(self):
        self.total_reward = 0
        self.illegal_moves = 0
        self.deaths = 0
        self.steps = 0
        self.episodes = []
        self.last_episode_cluster = []
        self.episodes_cluster_size = N_EPISODES / 1000

    def log(self, reward, is_legal_move, agent_is_dead):
        if not is_legal_move:
            self.illegal_moves += 1

        if agent_is_dead:
            self.deaths += 1

        self.total_reward += reward
        self.steps += 1

    def new_episode(self, epsilon, distance, q_table, observation):
        self.last_episode_cluster.append(
            {
                "deaths": self.deaths,
                "illegal_moves": self.illegal_moves,
                "reward": self.total_reward,
                "epsilon": epsilon,
                "steps_to_distance": distance / self.steps,
                "stuck_positions": calculate_stuck_positions(q_table, observation),
            }
        )

        self.deaths = 0
        self.illegal_moves = 0
        self.total_reward = 0
        self.steps = 0

        if len(self.last_episode_cluster) >= self.episodes_cluster_size:
            self.episodes.append(
                {
                    "deaths": np.mean(
                        [episode["deaths"] for episode in self.last_episode_cluster]
                    ),
                    "illegal_moves": np.mean(
                        [
                            episode["illegal_moves"]
                            for episode in self.last_episode_cluster
                        ]
                    ),
                    "epsilon": np.mean(
                        [episode["epsilon"] for episode in self.last_episode_cluster]
                    ),
                    "reward": np.mean(
                        [episode["reward"] for episode in self.last_episode_cluster]
                    ),
                    "steps_to_distance": np.mean(
                        [
                            episode["steps_to_distance"]
                            for episode in self.last_episode_cluster
                        ]
                    ),
                    "stuck_positions": np.mean(
                        [
                            episode["stuck_positions"]
                            for episode in self.last_episode_cluster
                        ]
                    ),
                }
            )
            self.last_episode_cluster = []

    def save(self):
        if not LEARN:
            return

        ep_nr = range(len(self.episodes))
        fig, axs = plt.subplots(3, 2, figsize=(14, 10))
        fig.suptitle("Training Metrics Per Episode", fontsize=16)

        # 1. Total reward
        axs[0, 0].plot(
            ep_nr,
            [episode["reward"] for episode in self.episodes],
            label="Reward",
            alpha=0.6,
        )
        axs[0, 0].set_title("Total Reward per Episode")
        axs[0, 0].set_xlabel("Episode")
        axs[0, 0].set_ylabel("Reward")

        # 2. Illegal moves
        axs[0, 1].plot(
            ep_nr,
            [episode["illegal_moves"] for episode in self.episodes],
            label="Illegal Moves",
            color="red",
            alpha=0.6,
        )
        axs[0, 1].set_title("Illegal Moves per Episode")
        axs[0, 1].set_xlabel("Episode")
        axs[0, 1].set_ylabel("Illegal Moves")

        # 3. Deaths
        axs[1, 0].plot(
            ep_nr,
            [episode["deaths"] for episode in self.episodes],
            label="Deaths",
            color="black",
            alpha=0.6,
        )
        axs[1, 0].set_title("Deaths per Episode")
        axs[1, 0].set_xlabel("Episode")
        axs[1, 0].set_ylabel("Deaths")

        # 4. Epsilon decay
        axs[1, 1].plot(
            ep_nr,
            [episode["epsilon"] for episode in self.episodes],
            label="Epsilon",
            color="green",
            alpha=0.6,
        )
        axs[1, 1].set_title("Exploration Rate (Epsilon)")
        axs[1, 1].set_xlabel("Episode")
        axs[1, 1].set_ylabel("Epsilon")

        # 5. Steps-to-distance ratio (lower is more efficient)
        axs[2, 0].plot(
            ep_nr,
            [episode["steps_to_distance"] for episode in self.episodes],
            label="Steps/Distance",
            color="purple",
            alpha=0.6,
        )
        axs[2, 0].set_title("Efficiency (Steps-to-Distance)")
        axs[2, 0].set_xlabel("Episode")
        axs[2, 0].set_ylabel("Ratio")

        # 6. Stuck positions
        axs[2, 1].plot(
            ep_nr,
            [episode["stuck_positions"] for episode in self.episodes],
            label="Stuck Positions",
            color="orange",
            alpha=0.6,
        )
        axs[2, 1].set_title("Stuck Positions")
        axs[2, 1].set_xlabel("Episode")
        axs[2, 1].set_ylabel("Stuck Positions")

        for ax in axs.flat:
            ax.grid(True)
            ax.legend()

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.legend()
        plt.savefig(
            f"metrics/metrics.dr={config.distance_reward}.tsp={config.time_step_punishment}.N={N_EPISODES}.im={config.illeagal_move_punishment}.fer={config.fire_extinguished_reward}.df={config.discount_factor}.png.png"
        )
        plt.close()


def calculate_stuck_positions(q_table, observation):
    action_deltas = {
        0: (0, -1),  # UP
        1: (0, 1),  # DOWN
        2: (-1, 0),  # LEFT
        3: (1, 0),  # RIGHT
        4: (0, 0),  # PUT OUT FIRE
    }
    states = q_table[observation[1][0]][observation[1][1]][1 if observation[2] else 0]

    positions = 0
    for x in range(config.grid_size):
        for y in range(config.grid_size):
            best_action = np.argmax(states[x, y])
            dx, dy = action_deltas[best_action]
            nx, ny = x + dx, y + dy

            if 0 <= nx < config.grid_size and 0 <= ny < config.grid_size:
                reverse_action = np.argmax(states[nx, ny])
                rdx, rdy = action_deltas[reverse_action]
                rx, ry = nx + rdx, ny + rdy

                if (rx, ry) == (x, y):
                    positions += 1

    return positions / 2
