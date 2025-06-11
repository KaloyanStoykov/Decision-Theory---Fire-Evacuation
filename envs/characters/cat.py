import numpy as np
from envs.ui.sprites import sprite_map
from envs.tiles.base import Base

STATE_COUNT = len(sprite_map["cat"])


class Cat(Base):
    _anim_state = 0

    def __init__(self, location: np.ndarray):
        x, y = location
        super().__init__(x, y)
        self.location = location

    def draw(self, canvas):
        self._anim_state = (self._anim_state + 1) % STATE_COUNT
        self._set_image(sprite_map["cat"][self._anim_state])
        super().draw(canvas)
