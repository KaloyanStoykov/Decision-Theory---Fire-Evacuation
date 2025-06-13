# envs/characters/firefighter.py

import numpy as np
from envs.constants import Action, config
from envs.ui.sprites import sprite_map
from envs.tiles.base import Base


class FireFighter(Base):
    _anim_state = 0
    is_alive = True

    def __init__(self, location: np.ndarray):
        self.location = location
        super().__init__(location[0], location[1])
        self._death_state_count = len(sprite_map["firefighter"]["dying"])
        self._idle_state_count = len(sprite_map["firefighter"]["idle"])
        self._anim_state = 0  # Current frame of animation
        self.is_dead = False

        # For movement animation
        self._target_location = np.copy(self.location)
        self._start_location = np.copy(self.location)
        self._move_progress = 1.0  # 0.0 to 1.0, 1.0 means standing still
        self._move_speed = 0.1  # How fast the movement animation plays

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
            self._move_progress = 0.0  # Start movement animation
            self.is_animating = True  # <--- NEW: Set animation flag

            # Update actual location immediately for game logic,
            # but rendering will interpolate.
            self.location = new_location
            self.x, self.y = self.location[0], self.location[1]

    def kill(self):
        self._anim_state = 1
        self.is_alive = False

    def draw(self, canvas):
        if self.is_alive:
            self._set_image(sprite_map["firefighter"]["idle"][self._anim_state])
        else:
            if self._anim_state < self._death_state_count - 1:
                self._set_image(sprite_map["firefighter"]["dying"][self._anim_state])

        return super().draw(canvas)

    def animate(self):
        if self.is_alive:
            self._anim_state = (self._anim_state + 1) % self._idle_state_count
        else:
            if self._anim_state < self._death_state_count - 1:
                self._anim_state += 1
            else:
                self._anim_state = 0
        """Sets the firefighter to a 'dead' state and starts death animation."""
        if not self.is_dead:
            self.is_dead = True
            self._anim_state = 0  # Start death animation from beginning
