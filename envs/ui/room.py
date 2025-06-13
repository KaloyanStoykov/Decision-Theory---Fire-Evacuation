from envs.constants import config, FloorType
from envs.tiles.floor import Floor


class RoomFactory:
    def create_walls(self, grid):
        pass

    def lay_floors(self, grid):
        for x in range(config.grid_size):
            for y in range(config.grid_size):
                if not grid.tiles[x][y]:
                    grid.tiles[x][y] = Floor(
                        x,
                        y,
                        grid.tiles,
                        FloorType.PURPLE if x < 4 and y < 4 else FloorType.BLUE,
                    )

    def create_items(self, grid):
        pass
