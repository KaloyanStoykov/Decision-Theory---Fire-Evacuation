import os
import numpy as np
from envs.constants import Action, Observation, config
from q_learning.debug import Visualizer

from q_learning.constants import (
    DISCOUNT_FACTOR,
    SAVE_Q_TABLE,
    LEARNING_RATE,
    EPSILON_DECAY,
    FINAL_EPSILON,
    INITIAL_EPSILON,
    FILE_NAME,
    DEBUG,
)


visualizer = Visualizer(
    grid_shape=(config.grid_size, config.grid_size), num_actions=len(Action)
)


def get_values(q_table, observation):
    return q_table[observation[1][0]][observation[1][1]][1 if observation[2] else 0][
        observation[0][0]
    ][observation[0][1]]


class Agent:
    epsilon = INITIAL_EPSILON
    counter = 0

    def __init__(self):
        if not SAVE_Q_TABLE and os.path.exists(FILE_NAME):
            print("Loading Q-table from file...")
            self.q_table = np.load(FILE_NAME)
        else:
            self.q_table = np.zeros(
                [
                    config.grid_size,
                    config.grid_size,
                    2,
                    config.grid_size,
                    config.grid_size,
                    len(Action),
                ]
            )
            # target_x, target_y, is_fire_present, agent_x, agent_y, action

    def get_action(self, actions: list[Action], obs: Observation) -> int:
        """
        Returns the best action with probability (1 - epsilon)
        otherwise a random action with probability epsilon to ensure exploration.
        """
        if np.random.uniform(0, 1) < self.epsilon:
            return actions.sample()
        else:  # with probability (1 - epsilon) act greedily (exploit)
            return np.argmax(get_values(self.q_table, obs))

    def update(
        self,
        obs: Observation,
        action: int,
        reward: float,
        terminated: bool,
        next_obs: Observation,
    ):
        """Updates the Q-value of an action."""
        q_value = get_values(self.q_table, obs)[action]
        future_q_value = np.max(get_values(self.q_table, next_obs))

        temporal_difference = reward + DISCOUNT_FACTOR * future_q_value - q_value

        get_values(self.q_table, obs)[action] = max(
            min(q_value + LEARNING_RATE * temporal_difference, config.max_reward),
            config.min_reward,
        )

        if DEBUG:
            visualizer.update(
                self.q_table, self.epsilon, temporal_difference, obs[1], obs[2]
            )

    def decay_epsilon(self):
        self.epsilon = max(FINAL_EPSILON, self.epsilon - EPSILON_DECAY)

    def save(self):
        if SAVE_Q_TABLE:
            np.save(FILE_NAME, self.q_table)
