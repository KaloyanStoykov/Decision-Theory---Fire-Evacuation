import os
import matplotlib.pyplot as plt
from collections import defaultdict
import gymnasium as gym
import numpy as np
from envs.constants import Action, Observation, GRID_SIZE

# from constants import DISCOUNT_FACTOR, LEARNING_RATE, EPSILON_DECAY, FINAL_EPSILON

N_EPISODES = 100_000
START_EPSILON = 1.0
LEARNING_RATE = 0.01
INITIAL_EPSILON = START_EPSILON
EPSILON_DECAY = (START_EPSILON / (N_EPISODES / 2),)  # reduce the exploration over time
FINAL_EPSILON = (0.1,)
DISCOUNT_FACTOR = 0.95


def encode_observation(observation):
    return observation[0] * GRID_SIZE + observation[1]


class Agent:
    def __init__(self, env: gym.Env):
        self.env = env
        self.error_plot_initialized = False
        if os.path.exists("q_table.npy"):
            self.q_table = np.load("q_table.npy")
        else:
            self.q_table = np.zeros([GRID_SIZE * GRID_SIZE, env.action_space.n])
        self.epsilon = INITIAL_EPSILON
        self.training_error = []

    def get_action(self, actions: list[Action], obs: Observation = None) -> int:
        """
        Returns the best action with probability (1 - epsilon)
        otherwise a random action with probability epsilon to ensure exploration.
        """
        if np.random.uniform(0, 1) < self.epsilon:
            return actions.sample()
        else:  # with probability (1 - epsilon) act greedily (exploit)
            return int(np.argmax(self.q_table[obs]))

    def update(
        self,
        obs: Observation,
        action: int,
        reward: float,
        terminated: bool,
        next_obs: Observation,
    ):
        """Updates the Q-value of an action."""
        q_value = self.q_table[encode_observation(obs)][action]
        future_q_value = np.max(self.q_table[encode_observation(next_obs)])

        temporal_difference = reward + DISCOUNT_FACTOR * future_q_value - q_value

        self.q_table[encode_observation(obs)][action] = (
            q_value + LEARNING_RATE * temporal_difference
        )
        self.training_error.append(temporal_difference)

        if len(self.training_error) % 10 == 0:
            self.update_plot()

    def update_plot(self):
        if not self.error_plot_initialized:
            plt.ion()
            self.fig, self.ax = plt.subplots()
            (self.line,) = self.ax.plot(self.training_error, label="TD Error")
            self.ax.set_xlabel("Step")
            self.ax.set_ylabel("Error")
            self.ax.set_title("TD Error (Live)")
            self.ax.legend()
            self.ax.grid(True)
            self.error_plot_initialized = True
        else:
            self.line.set_ydata(self.training_error)
            self.line.set_xdata(range(len(self.training_error)))
            self.ax.relim()
            self.ax.autoscale_view()
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()

    def decay_epsilon(self):
        self.epsilon = max(FINAL_EPSILON, self.epsilon - EPSILON_DECAY)

    def save(self):
        np.save("q_table.npy", self.q_table)
