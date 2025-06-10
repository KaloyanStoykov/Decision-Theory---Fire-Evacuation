import pygame
from envs.tiles.tile import Tile
from envs.sprites import sprite_map
from envs.constants import (
    CHANCE_OF_WALL_BEING_WINDOW,
    CHANCE_OF_WALL_BEING_PICTURE,
)
from envs.utilities import decide_action


def is_tile_above_wall(tiles, x, y):
    return y > 0 and isinstance(tiles[x][y - 1], Wall)


def is_tile_below_empty(tiles, x, y):
    return y == len(tiles) or isinstance(tiles[x][y + 1], Wall)


class Wall(Tile):
    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self._set_image(sprite_map["wall"]["front"])

    def register_neighbors(self, tiles: list[list[Tile]]):

        if is_tile_below_empty(tiles, self.x, self.y):
            self._set_image(sprite_map["wall"]["top"])
        else:
            self._set_image(sprite_map["wall"]["front"])

            if is_tile_below_empty(tiles, self.x, self.y) and decide_action(
                CHANCE_OF_WALL_BEING_PICTURE
            ):
                self._set_image(sprite_map["picture"])
            elif (
                not is_tile_above_wall(tiles, self.x, self.y)
                and is_tile_below_empty(tiles, self.x, self.y)
                and decide_action(CHANCE_OF_WALL_BEING_WINDOW)
            ):
                self._set_image(sprite_map["window"])

    def set_on_fire(self):
        raise Exception("Wall is not inflammable")

    def _set_image(self, img):
        if self.x % 2 == 0:
            img = pygame.transform.flip(img, True, False)

        return super()._set_image(img)
