import pygame
from envs.tiles.tile import Tile
from envs.sprites import sprite_map
from envs.constants import CHANCE_OF_WALL_BEING_WINDOW, CHANCE_OF_WALL_BEING_PICTURE
from envs.utilities import decide_action

class Wall(Tile):
  def __init__(self, x: int, y: int, state_tile, size: int):
    super().__init__(x, y, state_tile, False, False)
    self.sprite_size = size
    self.set_image(sprite_map["wall"]["front"])
    self.update_state()
  
  def register_neighbors(self, tiles: list[list[Tile]], x: int, y: int):
    if x < len(tiles) - 1 and isinstance(tiles[x + 1][y], Wall):
      self.set_image(sprite_map["wall"]["top"])
    else:
      self.set_image(sprite_map["wall"]["front"])

      if decide_action(CHANCE_OF_WALL_BEING_PICTURE):
        self.set_image(sprite_map["picture"])
        return

      if x != 0 and isinstance(tiles[x - 1][y], Wall):
        return
      
      if decide_action(CHANCE_OF_WALL_BEING_WINDOW):
        self.set_image(sprite_map["window"])

      
  def set_on_fire(self):
    raise Exception("Wall is not inflammable")
  
  def serialize(self):
    return {
      **super().serialize(),
      "type": "wall"
    }
  
  def set_image(self, img):
    if self.y % 2 == 0:
      img = pygame.transform.flip(img, True, False)
    
    return super().set_image(img, self.sprite_size)