import numpy as np
from envs.ui.room import RoomFactory
from envs.tiles.item import Item, Items
from envs.tiles.wall import Wall


class TrainingRoom(RoomFactory):
    def create_walls(self, grid):
        super().create_walls(grid)

        positions = [
            (0, 2),
            (1, 2),
            (1, 3),
            (2, 3),
            (3, 3),
            (3, 0),
            (3, 1),
        ]

        for pos in positions:
            grid.tiles[pos[0]][pos[1]] = Wall(pos[0], pos[1])

        for pos in positions:
            grid.tiles[pos[0]][pos[1]].register_neighbors(grid.tiles)

    def create_items(self, grid):
        super().create_items(grid)

        grid.tiles[0][3] = Item(grid.tiles[0][3], Items.BOOKSHELF_FULL)
        grid.tiles[1][0] = Item(grid.tiles[1][0], Items.BED_RED)
        grid.tiles[2][0] = Item(grid.tiles[2][0], Items.POT_GREEN)
