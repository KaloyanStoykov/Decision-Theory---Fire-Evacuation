# envs/characters/cat.py

import numpy as np
from envs.constants import config
from envs.ui.sprites import sprite_map
from envs.tiles.base import Base


class Cat(Base):
    _anim_state = 0

    def __init__(self, location: np.ndarray):
        self.location = location
        self._state_count = len(sprite_map["cat"])
        self._current_sprite_key = "idle"  # Default sprite key

        self._anim_state = 0  # Current frame of animation
        self._anim_speed = 0.1  # How fast animation frames change
        self.is_animating = False  # <--- NEW: Animation flag

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
        self._anim_state = (self._anim_state + 1) % self._state_count
        return super().animate()

    def draw(self, canvas):
        self._set_image(sprite_map["cat"][self._anim_state])
        return super().draw(canvas)
