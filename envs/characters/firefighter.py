# envs/characters/firefighter.py

import numpy as np
from envs.constants import Action, config
from envs.ui.sprites import sprite_map
import pygame

class FireFighter:
    def __init__(self, location: np.ndarray):
        self.location = location
        self.x, self.y = self.location[0], self.location[1]
        self._current_sprite_key = "idle" # Default sprite key
        self._anim_state = 0 # Current frame of animation
        self._anim_speed = 0.2 # How fast animation frames change
        self.is_dead = False
        self.is_animating = False # <--- NEW: Animation flag

        # For movement animation
        self._target_location = np.copy(self.location)
        self._start_location = np.copy(self.location)
        self._move_progress = 1.0 # 0.0 to 1.0, 1.0 means standing still
        self._move_speed = 0.1 # How fast the movement animation plays

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

    def move(self, new_location: np.ndarray):
        """Initiates a move animation to a new location."""
        if not np.array_equal(self.location, new_location):
            self._start_location = np.copy(self.location)
            self._target_location = np.copy(new_location)
            self._move_progress = 0.0 # Start movement animation
            self.is_animating = True # <--- NEW: Set animation flag

            # Update actual location immediately for game logic,
            # but rendering will interpolate.
            self.location = new_location
            self.x, self.y = self.location[0], self.location[1]

    def kill(self):
        """Sets the firefighter to a 'dead' state and starts death animation."""
        if not self.is_dead:
            self.is_dead = True
            self._current_sprite_key = "death"
            self._anim_state = 0 # Start death animation from beginning
            self.is_animating = True # <--- NEW: Set animation flag

    def animate(self):
        """
        Updates the animation state of the firefighter.
        Handles movement interpolation and sprite animation.
        """
        self.is_animating = False # Assume no animation unless specifically active

        if self.is_dead:
            if self._anim_state < len(sprite_map["firefighter"]["death"]) - 1:
                self._anim_state += self._anim_speed
                self.is_animating = True
            else:
                self._current_sprite_key = "death_final" # Stay on final death frame
                self._anim_state = len(sprite_map["firefighter"]["death"]) - 1
        elif self._move_progress < 1.0:
            self._move_progress += self._move_speed
            if self._move_progress >= 1.0:
                self._move_progress = 1.0
                self.is_animating = False # Movement animation finished
            else:
                self.is_animating = True # Movement ongoing
            # For movement, sprite might change (e.g., walk cycle)
            # You might want different sprites based on direction and _anim_state
            # For simplicity, keeping it idle or a generic walk sprite for now.
            self._current_sprite_key = "walk" # Example: change to 'walk' during movement
            self._anim_state = (self._anim_state + self._anim_speed) % len(sprite_map["firefighter"]["walk"])
        else:
            # If not moving or dead, return to idle animation
            self._current_sprite_key = "idle"
            self._anim_state = (self._anim_state + self._anim_speed) % len(sprite_map["firefighter"]["idle"])

    def draw(self, canvas: pygame.Surface):
        """Draws the firefighter on the canvas with appropriate animation frame."""
        sprite_list = sprite_map["firefighter"][self._current_sprite_key]
        if not sprite_list:
            print(f"Warning: No sprites found for firefighter key: {self._current_sprite_key}")
            return

        current_frame_idx = int(self._anim_state)
        if current_frame_idx >= len(sprite_list):
            current_frame_idx = len(sprite_list) - 1 # Clamp to last frame

        current_sprite = sprite_list[current_frame_idx]

        # Calculate interpolated position for smooth movement rendering
        interp_x = self._start_location[0] + (self._target_location[0] - self._start_location[0]) * self._move_progress
        interp_y = self._start_location[1] + (self._target_location[1] - self._start_location[1]) * self._move_progress

        canvas.blit(
            current_sprite,
            (
                int(interp_x * config.square_size),
                int(interp_y * config.square_size),
            ),
        )