# envs/characters/cat.py

import numpy as np
from envs.constants import config
from envs.ui.sprites import sprite_map
import pygame

class Cat:
    def __init__(self, location: np.ndarray):
        self.location = location
        self.x, self.y = self.location[0], self.location[1]
        self._current_sprite_key = "idle" # Default sprite key
        self._anim_state = 0 # Current frame of animation
        self._anim_speed = 0.1 # How fast animation frames change
        self.is_animating = False # <--- NEW: Animation flag

    @property
    def x(self):
        return self.location[0]

    @x.setter
    def x(self, value):
        self.location[0] = value

    @property
    def y(self):
        return self.location[1]

    @y.setter
    def y(self, value):
        self.location[1] = value

    def animate(self):
        """Updates the animation state of the cat."""
        self.is_animating = False # Assume no animation unless specifically active

        # Cat might have an idle animation or other special animations
        if self._current_sprite_key == "idle":
            self._anim_state = (self._anim_state + self._anim_speed) % len(sprite_map["cat"]["idle"])
            # If idle animation has multiple frames, it's animating
            if len(sprite_map["cat"]["idle"]) > 1:
                self.is_animating = True
        # Add other animation states (e.g., scared, rescued) if needed

    def draw(self, canvas: pygame.Surface):
        """Draws the cat on the canvas with appropriate animation frame."""
        sprite_list = sprite_map["cat"][self._current_sprite_key]
        if not sprite_list:
            print(f"Warning: No sprites found for cat key: {self._current_sprite_key}")
            return

        current_frame_idx = int(self._anim_state)
        if current_frame_idx >= len(sprite_list):
            current_frame_idx = len(sprite_list) - 1 # Clamp to last frame

        current_sprite = sprite_list[current_frame_idx]

        canvas.blit(
            current_sprite,
            (
                int(self.x * config.square_size),
                int(self.y * config.square_size),
            ),
        )