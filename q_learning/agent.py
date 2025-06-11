import matplotlib.pyplot as plt
import os
import numpy as np
from envs.constants import Action, Observation, config
from q_learning.debug import Visualizer

from q_learning.constants import (
    DISCOUNT_FACTOR,
    LEARNING_RATE,
    EPSILON_DECAY,
    FINAL_EPSILON,
    INITIAL_EPSILON,
    FILE_NAME,
    DEBUG,
    DEBUG_UPDATE,
)


visualizer = Visualizer(
    grid_shape=(config.grid_size, config.grid_size), num_actions=len(Action)
)


def encode_observation(observation):
    return observation[0] * config.grid_size + observation[1]


class Agent:
    epsilon = INITIAL_EPSILON
    counter = 0

    def __init__(self):
        if os.path.exists(FILE_NAME):
            self.q_table = np.load(FILE_NAME)
        else:
            self.q_table = np.zeros([config.grid_size * config.grid_size, len(Action)])

    def get_action(self, actions: list[Action], obs: Observation) -> int:
        """
        Returns the best action with probability (1 - epsilon)
        otherwise a random action with probability epsilon to ensure exploration.
        """
        if np.random.uniform(0, 1) < self.epsilon:
            return actions.sample()
        else:  # with probability (1 - epsilon) act greedily (exploit)
            action = np.argmax(self.q_table[encode_observation(obs)])

            return action

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

        if not DEBUG:
            return

        self.counter += 1
        if self.counter == DEBUG_UPDATE:
            self.counter = 0
            visualizer.update(self.q_table, self.epsilon, temporal_difference)

    def decay_epsilon(self):
        self.epsilon = max(FINAL_EPSILON, self.epsilon - EPSILON_DECAY)

    def save(self):
        np.save(FILE_NAME, self.q_table)
