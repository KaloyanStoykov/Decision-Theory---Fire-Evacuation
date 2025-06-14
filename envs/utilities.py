import numpy as np
from envs.tiles.tile import Tile
from envs.tiles.base import Base
from envs.constants import config


def decide_action(chance):
    return np.random.rand() < chance


def random_tile(
    tiles: list[list[Tile]],
    target: Base,
    agent: Base,
    inflammable: bool | None = None,
    burning: bool | None = None,
) -> Tile | None:
    possible_tiles: list[Tile] = []
    for row in tiles:
        for tile in row:
            if not is_occupied(tile, target) and not is_occupied(tile, agent):
                possible_tiles.append(tile)

    if inflammable is not None:
        possible_tiles = [
            tile for tile in possible_tiles if tile.is_inflammable == inflammable
        ]

    if burning is not None:
        possible_tiles = [tile for tile in possible_tiles if tile.is_on_fire == burning]

    if not possible_tiles:
        return None

    return np.random.choice(possible_tiles)


def is_occupied(tile: Tile, entity: Base):
    return tile.x == entity.x and tile.y == entity.y


def out_of_grid(pos: tuple[int]):
    return (
        pos[0] < 0
        or pos[0] >= config.grid_size
        or pos[1] < 0
        or pos[1] >= config.grid_size
    )
