import numpy as np
from envs.ui.sprites import sprite_map
from envs.tiles.base import Base


class Cat(Base):
    _anim_state = 0

    def __init__(self, location: np.ndarray):
        x, y = location
        super().__init__(x, y)
        self.location = location
        self._state_count = len(sprite_map["cat"])

    def draw(self, canvas):
        self._set_image(sprite_map["cat"][self._anim_state])
        super().draw(canvas)

    def animate(self):
        self._anim_state = (self._anim_state + 1) % self._state_count
        return super().animate()
