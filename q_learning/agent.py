from collections import defaultdict
import gymnasium as gym
import numpy as np
from envs.constants import Action

# from constants import DISCOUNT_FACTOR, LEARNING_RATE, EPSILON_DECAY, FINAL_EPSILON

N_EPISODES = 100_000
START_EPSILON = 1.0
LEARNING_RATE = (0.01,)
INITIAL_EPSILON = START_EPSILON
EPSILON_DECAY = (START_EPSILON / (N_EPISODES / 2),)  # reduce the exploration over time
FINAL_EPSILON = (0.1,)
DISCOUNT_FACTOR = 0.95


class Agent:
    def __init__(self, env: gym.Env):
        self.env = env
        self.q_table = np.zeros([len(env.observation_space), env.action_space.n])
        self.epsilon = INITIAL_EPSILON
        self.training_error = []

    def get_action(
        self, actions: list[Action], obs: tuple[int, int, bool] = None
    ) -> int:
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
        obs: tuple[int, int, bool],
        action: int,
        reward: float,
        terminated: bool,
        next_obs: tuple[int, int, bool],
    ):
        """Updates the Q-value of an action."""
        q_value = self.q_table[obs][action]
        future_q_value = np.max(self.q_table[next_obs])

        temporal_difference = reward + DISCOUNT_FACTOR * future_q_value - q_value

        self.q_table[obs][action] = q_value + LEARNING_RATE * temporal_difference
        self.training_error.append(temporal_difference)

    def decay_epsilon(self):
        self.epsilon = max(FINAL_EPSILON, self.epsilon - EPSILON_DECAY)
