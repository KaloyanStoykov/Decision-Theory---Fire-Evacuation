from envs.constants import FloorType, Side
from envs.tiles.tile import Tile
import envs.sprites as sprites

def get_sprite_from_borders(sprite_map: dict, borders: list[Side]):
  if len(borders) == 0:
    return sprite_map["middle_center"]["without_middle"]

  categories = []
  
  if Side.TOP in borders:
    categories.append("top")
  if Side.BOTTOM in borders:
    categories.append("bottom")
  if Side.RIGHT in borders:
    categories.append("right")
  if Side.LEFT in borders:
    categories.append("left")
    
  if len(categories) == 1:
    if categories[0] == "top" or categories[0] == "bottom": 
      return sprite_map[categories[0] + "_center"]["without_middle"]
    else:
      return sprite_map["middle_" + categories[0]]["without_middle"]
      
  category_name = "_".join(categories)
  
  if category_name not in sprite_map:
    raise Exception(f"Floor with category '{category_name}' not found")

  if len(categories) == 2:
    return sprite_map[category_name]["without_middle"]

  return sprite_map[category_name]
 
class Floor(Tile):
  def __init__(self, type: FloorType, size: int, borders: list[Side] = []):
    super().__init__(True, True)
    
    if type == FloorType.TILE:
      self.set_image(sprites.sprite_map["floor_tile"], size)
      return
    
    color = None
    match type:
      case FloorType.BLUE:
        color = "blue"
      case FloorType.RED:
        color = "red"
      case FloorType.PURPLE:
        color = "purple"
      case _:
        raise Exception(f"Floor with type {type} not found")
    
    self.set_image(get_sprite_from_borders(sprites.sprite_map[color + "_carpet"], borders), size)
    