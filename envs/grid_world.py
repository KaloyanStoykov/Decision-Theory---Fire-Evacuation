import gymnasium as gym
from gymnasium import spaces
import numpy as np
from envs.grid import Grid
from envs.constants import Action, config
from envs.ui.window import Window
from envs.ui.training_room import TrainingRoom


class FireFighterWorld(gym.Env):
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": config.fps}

    def __init__(self, static_mode=False, render_mode=None):
        self.grid = None  # Will be initialized in reset
        self.static_mode = static_mode

        self.observation_space = spaces.Tuple(
            (
                spaces.Box(0, config.grid_size - 1, shape=(2,), dtype=int),  # agent
                spaces.Box(0, config.grid_size - 1, shape=(2,), dtype=int),  # target
                spaces.Discrete(2),  # is_fire_present
            )
        )

        self.action_space = spaces.Discrete(len(Action))

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        self.window = Window() if self.render_mode == "human" else None

    def _get_obs(self):
        return (
            self.grid.agent.location,
            self.grid.target.location,
            self.grid.tiles[3][2].is_on_fire,
        )

    def _get_info(self, is_legal_move=True):
        return {
            "is_legal_move": is_legal_move,
            "is_agent_dead": self.grid.is_agent_dead(),
            "distance": np.linalg.norm(
                self.grid.agent.location - self.grid.target.location
            ),
        }

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        # options can now include 'initial_agent_pos' and 'initial_target_pos' for MDP
        initial_agent_pos = None
        initial_target_pos = None
        if options and "initial_agent_pos" in options:
            initial_agent_pos = options["initial_agent_pos"]
        if options and "initial_target_pos" in options:
            initial_target_pos = options["initial_target_pos"]

        # Re-create grid with specified initial positions if in static mode for MDP
        self.grid = Grid(
            TrainingRoom(),
            self.static_mode,
            initial_agent_pos,
            initial_target_pos,
            self.np_random,
        )

        if self.render_mode == "human":
            self._render_frame()

        return self._get_obs(), self._get_info()

    def step(self, action):
        is_legal_move = self.grid.update(list(Action)[action])

        reward = config.time_step_punishment + config.distance_reward * (
            config.max_distance
            - np.linalg.norm(self.grid.agent.location - self.grid.target.location)
        )

        terminated = False

        if not is_legal_move:
            reward += config.illeagal_move_punishment
        elif self.grid.is_agent_dead():
            terminated = True
            reward += config.death_punishment
        elif self.grid.is_cat_rescued():
            terminated = True
            reward += config.evacuation_success_reward
        elif action == Action.PUT_OUT_FIRE.value:
            reward += config.fire_extinguished_reward

        if self.render_mode == "human":
            self._render_frame()

        return (
            self._get_obs(),
            max(min(reward, config.max_reward), config.min_reward),  # clip reward
            terminated,
            False,
            self._get_info(is_legal_move),
        )

    def render(self):
        if self.render_mode != "human":
            return

        # Ensure animation completes if agent dies
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
