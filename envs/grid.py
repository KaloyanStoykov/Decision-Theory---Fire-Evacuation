import numpy as np
from envs.constants import FloorType, CHANCE_OF_CATCHING_FIRE, CHANCE_OF_SELF_EXTINGUISH
from envs.tiles.tile import Tile
from envs.tiles.wall import Wall
from envs.tiles.item import Item, Items
from envs.tiles.floor import Floor, Side
from envs.utilities import decide_action, random_tile

def get_borders(tiles: list[list[Tile]], x, y):
  sides: list[Side] = []
  
  if y > 0 and isinstance(tiles[y - 1][x], Wall):
    sides.append(Side.TOP)
  if x < len(tiles[0]) - 1 and isinstance(tiles[y][x + 1], Wall):
    sides.append(Side.RIGHT)
  if y < len(tiles) - 1 and isinstance(tiles[y + 1][x], Wall):
    sides.append(Side.BOTTOM)
  if x > 0 and isinstance(tiles[y][x - 1], Wall):
    sides.append(Side.LEFT)
  
  return sides

class Grid:
  def __init__(self, size, tile_size: int):
    self.size = size
    self.create_grid(tile_size)
  
  def create_grid(self, tile_size: int):
    self.tiles: list[list[Tile]] = [[None for _ in range(self.size)] for _ in range(self.size)]
    
    # First Walls
    self.tiles[1][4] = Wall(tile_size)
    self.tiles[2][4] = Wall(tile_size)
    self.tiles[2][3] = Wall(tile_size)
    self.tiles[3][4] = Wall(tile_size)
    self.tiles[1][3] = Wall(tile_size)
    
    # Then Floors so they are aware of the walls
    for y in range(self.size):
      for x in range(self.size):
        if not self.tiles[y][x]:
          self.tiles[y][x] = Floor(FloorType.BLUE, tile_size, get_borders(self.tiles, x, y))
        elif isinstance(self.tiles[y][x], Wall):
          self.tiles[y][x].register_neighbors(self.tiles, tile_size, x, y)

    # Then Items so they sit on a ready floor
    floor = self.random_empty_space()
    self.tiles[floor["x"]][floor["y"]] = Item(Items.TABLE, floor["tile"], tile_size)
  
  def update(self):
    if decide_action(CHANCE_OF_CATCHING_FIRE):
      tile = random_tile(self.tiles, inflammable=True)
      if tile:
        tile.set_on_fire()
      
    if decide_action(CHANCE_OF_SELF_EXTINGUISH):
      tile = random_tile(self.tiles, burning=True)
      if tile:
        tile.put_out_fire()

  def draw(self, canvas, square_size):
    for y, row in enumerate(self.tiles):
      for x, tile in enumerate(row):
        tile.draw(canvas, square_size, x, y)
  
  def random_empty_space(self):
    possible_tiles = []
    
    for y in range(len(self.tiles)):
      for x in range(len(self.tiles[0])):
        if isinstance(self.tiles[y][x], Floor):
          possible_tiles.append({
            "tile": self.tiles[y][x],
            "x": x,
            "y": y
          })
    
    if not possible_tiles:
      return None
    
    i = np.random.randint(0, len(possible_tiles))

    return possible_tiles[i]

    