import pygame
from envs.tiles.tile import Tile
from envs.sprites import sprite_map
from envs.constants import CHANCE_OF_WALL_BEING_WINDOW, CHANCE_OF_WALL_BEING_PICTURE
from envs.utilities import decide_action

class Wall(Tile):
  def __init__(self, size: int):
    super().__init__(False, False)
    self.set_image(sprite_map["wall"]["top"], size)
  
  def register_neighbors(self, tiles: list[list[Tile]], size: int, x: int, y: int):

    if y < len(tiles) - 1 and isinstance(tiles[y + 1][x], Wall):
      self.set_image(sprite_map["wall"]["top"], size)
    else:
      self.set_image(sprite_map["wall"]["front"], size)

      if decide_action(CHANCE_OF_WALL_BEING_PICTURE):
        self.set_image(sprite_map["picture"], size)
        return

      if y != 0 and isinstance(tiles[y - 1][x], Wall):
        return
      
      if decide_action(CHANCE_OF_WALL_BEING_WINDOW):
        self.set_image(sprite_map["window"], size)

      
  def set_on_fire(self):
    raise Exception("Wall is not inflammable")