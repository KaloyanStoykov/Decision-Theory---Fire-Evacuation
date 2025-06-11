import numpy as np
from envs.ui.sprites import sprite_map
from envs.tiles.base import Base

IDLE_STATE_COUNT = len(sprite_map["firefighter"]["idle"])
DEATH_STATE_COUNT = len(sprite_map["firefighter"]["dying"])


class FireFighter(Base):
    _anim_state = 0
    is_alive = True

    def __init__(self, location: np.ndarray):
        (x, y) = location
        super().__init__(x, y)
        self.location = location

    def move(self, x: int, y: int):
        self.x = x
        self.y = y
        self.location = np.array([self.x, self.y])

    def move(self, location: np.ndarray):
        self.x, self.y = location
        self.location = location

    def kill(self):
        self._anim_state = 1
        self.is_alive = False

    def draw(self, canvas):
        if self.is_alive:
            self._set_image(sprite_map["firefighter"]["idle"][self._anim_state])
        else:
            if self._anim_state < DEATH_STATE_COUNT - 1:
                self._set_image(sprite_map["firefighter"]["dying"][self._anim_state])

        return super().draw(canvas)

    def animate(self):
        if self.is_alive:
            self._anim_state = (self._anim_state + 1) % IDLE_STATE_COUNT
        else:
            if self._anim_state < DEATH_STATE_COUNT - 1:
                self._anim_state += 1
            else:
                self._anim_state = 0

        return super().animate()
