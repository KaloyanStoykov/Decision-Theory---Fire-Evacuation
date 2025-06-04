import numpy as np
from envs.tiles.tile import Tile

def decide_action(chance):
  return np.random.rand() < chance

def random_tile(tiles: list[list[Tile]], inflammable: bool | None = None, burning: bool | None = None) -> Tile | None:
  possible_tiles = [tile for row in tiles for tile in row]

  if inflammable is not None:
    possible_tiles = [tile for tile in possible_tiles if tile.is_inflammable == inflammable]
  
  if burning is not None:
    possible_tiles = [tile for tile in possible_tiles if tile.is_on_fire == burning]

  if not possible_tiles:
    return None
  
  return np.random.choice(possible_tiles)