import gymnasium as gym
from gymnasium import spaces
import pygame
import numpy as np
from envs.grid import Grid
from envs.constants import (
    Action,
    WINDOW_SIZE,
    GRID_SIZE,
    INITIAL_POINTS,
    ILLEAGAL_MOVE_PUNISHMENT,
    DEATH_PUNISHMENT,
)


class FireFighterWorld(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}

    def __init__(self, render_mode=None, size=5):
        self.grid = Grid(self.np_random)
        self.points = INITIAL_POINTS
        self.canvas = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE))
        self.canvas.fill((255, 255, 255))

        self.observation_space = spaces.Tuple(
            (
                spaces.Box(0, size - 1, shape=(2,), dtype=int),  # agent
                spaces.Box(0, size - 1, shape=(2,), dtype=int),  # target
                # "tiles": self.grid.tiles,
                spaces.Discrete(
                    int(
                        np.linalg.norm(
                            np.array([0, 0]) - np.array([size - 1, size - 1]), ord=1
                        )
                    )
                ),  # distance
            )
        )

        self.action_space = spaces.Discrete(4)
        self._action_to_direction = {
            Action.RIGHT.value: np.array([1, 0]),
            Action.UP.value: np.array([0, 1]),
            Action.LEFT.value: np.array([-1, 0]),
            Action.DOWN.value: np.array([0, -1]),
        }

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        if self.render_mode == "human":
            pygame.init()
            pygame.display.init()
            self.window = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
            self.clock = pygame.time.Clock()

    def _get_obs(self):
        return (
            self.grid.agent.location,
            self.grid.target.location,
            int(
                np.linalg.norm(
                    self.grid.agent.location - self.grid.target.location, ord=1
                )
            ),
        )

    def _get_info(self):
        return {}

    def get_possible_actions(self):
        return np.array(self.grid.get_possible_actions())

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.grid.create_grid(self.np_random)
        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, info

    def step(self, action):
        direction = self._action_to_direction[action]
        is_legal_move = self.grid.update(
            np.clip(self.grid.agent.location + direction, 0, GRID_SIZE - 1)
        )

        reward = self.points / INITIAL_POINTS
        terminated = False

        if not is_legal_move:
            reward = ILLEAGAL_MOVE_PUNISHMENT
        elif self.grid.is_agent_dead() or np.array_equal(
            self.grid.agent.location, self.grid.target.location
        ):
            terminated = True
            if self.grid.is_agent_dead():
                reward = DEATH_PUNISHMENT

        if self.render_mode == "human":
            self._render_frame()

        return self._get_obs(), reward, terminated, self._get_info()

    def render(self):
        if self.render_mode == "rgb_array":
            if self.grid.is_agent_dead():
                while self.grid.agent._anim_state != 0:
                    self._render_frame()
            else:
                self._render_frame()

    def _render_frame(self):
        self.grid.draw(self.canvas)
        self.window.blit(self.canvas, self.canvas.get_rect())

        pygame.event.pump()
        pygame.display.update()
        self.clock.tick(self.metadata["render_fps"])

    def close(self):
        if self.window is not None:
            pygame.display.quit()
            pygame.quit()
