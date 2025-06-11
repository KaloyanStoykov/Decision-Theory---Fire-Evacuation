import gymnasium as gym
from gymnasium import spaces
import numpy as np
from envs.grid import Grid
from envs.constants import Action, config
from envs.ui.window import Window


class FireFighterWorld(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": config.fps}

    def __init__(self, render_mode=None):
        self.grid = Grid(self.np_random)
        self.points = config.initial_points

        self.observation_space = spaces.Tuple(
            # (spaces.Box(0, size - 1, shape=(2,), dtype=int),)  # agent
            (
                spaces.Discrete(config.grid_size),
                spaces.Discrete(config.grid_size),
            )  # agent
        )

        self.action_space = spaces.Discrete(len(Action))

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        self.window = Window() if self.render_mode == "human" else None

    def _get_obs(self):
        return (self.grid.agent.x, self.grid.agent.y)

    def _get_info(self):
        return {}

    def get_possible_actions(self):
        return np.array(self.grid.get_possible_actions())

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        if seed is not None:
            self.grid = Grid(self.np_random)

        self.grid.create_grid()
        observation = self._get_obs()
        info = self._get_info()

        if self.render_mode == "human":
            self._render_frame()

        return observation, info

    def step(self, action):
        is_legal_move = self.grid.update(list(Action)[action])

        reward = self.points / config.initial_points
        terminated = False

        if not is_legal_move:
            reward = config.illeagal_move_punishment
        elif self.grid.is_agent_dead() or np.array_equal(
            self.grid.agent.location, self.grid.target.location
        ):
            terminated = True
            if self.grid.is_agent_dead():
                reward = config.death_punishment

        if self.render_mode == "human":
            self._render_frame()

        return self._get_obs(), reward, terminated, False, self._get_info()

    def render(self):
        if self.render_mode != "human":
            return

        if self.grid.is_agent_dead():
            while self.grid.agent._anim_state != 0:
                self._render_frame()
        else:
            self._render_frame()

    def _render_frame(self):
        self.window.draw(
            lambda canvas: self.grid.draw(canvas),
            lambda: self.grid.animate(),
        )

    def close(self):
        if self.window is not None:
            self.window.close()
