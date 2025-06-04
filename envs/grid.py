import numpy as np
from envs.constants import FloorType, CHANCE_OF_CATCHING_FIRE, CHANCE_OF_SELF_EXTINGUISH
from envs.tiles.tile import Tile
from envs.tiles.wall import Wall
from envs.tiles.item import Item, Items
from envs.tiles.floor import Floor, Side
from envs.utilities import decide_action, random_tile

def get_borders(tiles: list[list[Tile]], x, y):
  sides: list[Side] = []
  
  if x > 0 and isinstance(tiles[x - 1][y], Wall):
    sides.append(Side.TOP)
  if y < len(tiles[0]) - 1 and isinstance(tiles[x][y + 1], Wall):
    sides.append(Side.RIGHT)
  if x < len(tiles) - 1 and isinstance(tiles[x + 1][y], Wall):
    sides.append(Side.BOTTOM)
  if y > 0 and isinstance(tiles[x][y - 1], Wall):
    sides.append(Side.LEFT)
  
  return sides

class Grid:
  def __init__(self, size, tile_size: int):
    self.size = size
    self.create_grid(tile_size)
  
  def create_grid(self, tile_size: int):
    self.tiles: list[list[Tile]] = [[None for _ in range(self.size)] for _ in range(self.size)]
    self.state = [[{} for _ in range(self.size)] for _ in range(self.size)]
    
    # First Walls
    self.tiles[1][4] = Wall(1, 4, self.state[1][4], tile_size)
    self.tiles[2][4] = Wall(2, 4, self.state[2][4], tile_size)
    self.tiles[2][3] = Wall(2, 3, self.state[2][3], tile_size)
    self.tiles[3][4] = Wall(3, 4, self.state[3][4], tile_size)
    self.tiles[1][3] = Wall(1, 3, self.state[1][3], tile_size)
    
    # Then Floors so they are aware of the walls
    for y in range(self.size):
      for x in range(self.size):
        if not self.tiles[x][y]:
          self.tiles[x][y] = Floor(x, y, self.state[x][y], FloorType.BLUE, tile_size, get_borders(self.tiles, x, y))
        elif isinstance(self.tiles[x][y], Wall):
          self.tiles[x][y].register_neighbors(self.tiles, x, y)

    # Then Items so they sit on a ready floor
    floor = self.random_empty_space()
    self.tiles[floor.x][floor.y] = Item(floor.x, floor.y, self.state[floor.x][floor.y], Items.TABLE, floor, tile_size)
  
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
    
    for x in range(len(self.tiles)):
      for y in range(len(self.tiles[x])):
        if isinstance(self.tiles[x][y], Floor):
          possible_tiles.append(self.tiles[x][y])
    
    if not possible_tiles:
      return None
    
    return np.random.choice(possible_tiles)