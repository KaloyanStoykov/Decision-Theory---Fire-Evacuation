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
            (spaces.Box(0, config.grid_size - 1, shape=(2,), dtype=int),)  # agent
        )

        self.action_space = spaces.Discrete(len(Action))

        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        self.window = Window() if self.render_mode == "human" else None

    def _get_obs(self):
        return (self.grid.agent.location,)

    def _get_info(self):
        return {
            "agent_pos": self.grid.agent.location.tolist(),
            "target_pos": self.grid.target.location.tolist(),
            "is_agent_dead": self.grid.is_agent_dead(),
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
        # The grid's update method now handles the static_mode flag
        is_legal_move = self.grid.update(list(Action)[action])

        reward = config.time_step_punishment  # Default punishment for each step

        terminated = False

        if not is_legal_move:
            reward = config.illeagal_move_punishment  # Punish illegal moves immediately

        # Check for termination conditions *after* agent movement/action
        if self.grid.is_agent_dead():
            terminated = True
            reward = config.death_punishment  # Large negative reward for death
        elif np.array_equal(self.grid.agent.location, self.grid.target.location):
            terminated = True
            reward = (
                config.evacuation_success_reward
            )  # Large positive reward for reaching target

        # For the MDP, 'chance_of_catching_fire' and 'chance_of_self_extinguish' are 0 (static)
        # These are handled within grid.update and should be skipped if static_mode is True.
        # The Q-learning training setup sets chance_of_catching_fire to 0, which also
        # effectively makes fire static for Q-learning if that's desired for comparison.

        if self.render_mode == "human":
            self._render_frame()

        return self._get_obs(), reward, terminated, False, self._get_info()

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
