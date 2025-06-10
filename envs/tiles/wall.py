import pygame
from envs.tiles.tile import Tile
from envs.sprites import sprite_map
from envs.constants import (
    CHANCE_OF_WALL_BEING_WINDOW,
    CHANCE_OF_WALL_BEING_PICTURE,
    SQUARE_SIZE,
)
from envs.utilities import decide_action


class Wall(Tile):
    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self._set_image(sprite_map["wall"]["front"])

    def register_neighbors(self, tiles: list[list[Tile]]):
        if self.y > 0 and isinstance(tiles[self.x][self.y + 1], Wall):
            self._set_image(sprite_map["wall"]["top"])
        else:
            self._set_image(sprite_map["wall"]["front"])

            if decide_action(CHANCE_OF_WALL_BEING_PICTURE):
                self._set_image(sprite_map["picture"])
                return

            if self.y > len(tiles) - 1 and isinstance(tiles[self.x][self.y - 1], Wall):
                return

            if decide_action(CHANCE_OF_WALL_BEING_WINDOW):
                self._set_image(sprite_map["window"])

    def set_on_fire(self):
        raise Exception("Wall is not inflammable")

    def _set_image(self, img):
        if self.x % 2 == 0:
            img = pygame.transform.flip(img, True, False)

        return super()._set_image(img)
