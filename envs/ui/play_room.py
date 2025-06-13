from envs.ui.room import RoomFactory
from envs.tiles.item import Item, Items
from envs.tiles.wall import Wall


class PlayRoom(RoomFactory):
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
            (5, 0),
            (5, 1),
            (5, 2),
            (5, 3),
            (5, 4),
            (6, 4),
            (0, 6),
            (0, 7),
            (1, 7),
            (2, 7),
            (3, 7),
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

        grid.tiles[7][1] = Item(grid.tiles[7][1], Items.CHAIR_RED)
        grid.tiles[7][2] = Item(grid.tiles[7][2], Items.TABLE)

        floor = grid._random_empty_space()
        if not floor:
            return

        grid.tiles[floor.x][floor.y] = Item(floor, Items.RADIO)
