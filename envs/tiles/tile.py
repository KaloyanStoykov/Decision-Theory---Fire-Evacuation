from envs.ui.sprites import sprite_map
from envs.tiles.base import Base
from envs.constants import config


class Tile(Base):
    is_on_fire = False
    is_breakable = False
    is_traversable = False
    is_inflammable = False
    _fire_state = 1

    def __init__(self, x, y):
        super().__init__(x, y)
        self._fire_state_count = len(sprite_map["fires"])

    def set_on_fire(self):
        if not self.is_inflammable:
            raise Exception("Tile is not inflammable")

        self.is_on_fire = True
        self._fire_state = 0

    def put_out_fire(self):
        self.is_on_fire = False

    def draw(self, canvas):
        super().draw(canvas)

        if self.is_on_fire:
            self.draw_fire(canvas)

    def draw_fire(self, canvas):
        canvas.blit(
            sprite_map["fires"][self._fire_state - 1],
            (self.x * config.square_size, self.y * config.square_size),
        )

    def animate(self):
        if self.is_on_fire:
            self._fire_state = (self._fire_state + 1) % self._fire_state_count
