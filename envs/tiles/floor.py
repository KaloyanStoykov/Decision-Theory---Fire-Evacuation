from envs.constants import FloorType, Side
from envs.tiles.tile import Tile
from envs.tiles.wall import Wall
from envs.ui.sprites import sprite_map


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
        return (
            sprite_map[category_name]
            if not isinstance(sprite_map[category_name], dict)
            else sprite_map[category_name]["without_middle"]
        )

    return sprite_map[category_name]


def get_borders(tiles: list[list[Tile]], x, y):
    sides: list[Side] = []

    if y > 0 and isinstance(tiles[x][y - 1], Wall):
        sides.append(Side.TOP)
    if x < len(tiles[0]) - 1 and isinstance(tiles[x + 1][y], Wall):
        sides.append(Side.RIGHT)
    if y < len(tiles) - 1 and isinstance(tiles[x][y + 1], Wall):
        sides.append(Side.BOTTOM)
    if x > 0 and isinstance(tiles[x - 1][y], Wall):
        sides.append(Side.LEFT)

    return sides


class Floor(Tile):
    def __init__(self, x: int, y: int, tiles: list[list[Tile]], type: FloorType):
        super().__init__(x, y)
        self.is_traversable = True
        self.is_inflammable = True

        image = None
        match type:
            case FloorType.TILE:
                self._set_image(image)
                return

            case FloorType.BLUE:
                image = sprite_map["blue_carpet"]
            case FloorType.RED:
                image = sprite_map["red_carpet"]
            case FloorType.PURPLE:
                image = sprite_map["purple_carpet"]
            case _:
                raise Exception(f"Floor with type {type} not found")

        self._set_image(get_sprite_from_borders(image, get_borders(tiles, x, y)))
