import numpy as np
from envs.constants import (
    FloorType,
    CHANCE_OF_CATCHING_FIRE,
    CHANCE_OF_SELF_EXTINGUISH,
    Action,
    GRID_SIZE,
)
from envs.tiles.tile import Tile
from envs.tiles.wall import Wall
from envs.tiles.item import Item, Items
from envs.tiles.floor import Floor
from envs.utilities import decide_action, random_tile, is_occupied
from envs.cat import Cat
from envs.firefighter import FireFighter


class Grid:
    def __init__(self, np_random):
        self.create_grid(np_random)

    def create_grid(self, np_random):
        self.agent = FireFighter(np_random.integers(0, GRID_SIZE, size=2, dtype=int))
        target_location = self.agent.location
        while np.array_equal(target_location, self.agent.location):
            target_location = np_random.integers(0, GRID_SIZE, size=2, dtype=int)

        self.target = Cat(target_location)

        self.tiles: list[list[Tile]] = [
            [None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)
        ]

        self._create_walls()
        self._lay_floors()
        self._create_items()

    def _create_walls(self):
        positions = [
            (4, 1),
            (4, 2),
            (3, 2),
            (2, 3),
            (4, 3),
            (3, 1),
        ]

        for pos in positions:
            self.tiles[pos[0]][pos[1]] = Wall(pos[0], pos[1])

        for pos in positions:
            self.tiles[pos[0]][pos[1]].register_neighbors(self.tiles)

    def _lay_floors(self):
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                if not self.tiles[x][y]:
                    self.tiles[x][y] = Floor(
                        x,
                        y,
                        self.tiles,
                        FloorType.BLUE,
                    )

    def _create_items(self):
        floor = self.random_empty_space()
        if not floor:
            return

        self.tiles[floor.x][floor.y] = Item(floor, Items.RADIO)

    def is_agent_dead(self):
        return self.tiles[self.agent.x][self.agent.y].is_on_fire

    def update(self, next_agent_location: tuple[int, int]):
        if not self.tiles[next_agent_location[0]][
            next_agent_location[1]
        ].is_traversable:
            return False

        self.agent.move(next_agent_location)

        if self.is_agent_dead():
            self.agent.kill()

        for row in self.tiles:
            for tile in row:
                tile.update()

        if decide_action(CHANCE_OF_CATCHING_FIRE):
            tile = random_tile(self.tiles, self.target, self.agent, inflammable=True)
            if tile:
                tile.set_on_fire()

        if decide_action(CHANCE_OF_SELF_EXTINGUISH):
            tile = random_tile(self.tiles, self.target, self.agent, burning=True)
            if tile:
                tile.put_out_fire()

        return True

    def get_possible_actions(self):
        possible_actions = np.ones(len(Action), dtype=bool)
        possible_actions[Action.BreakDoor.value] = False

        left = self.tiles[self.agent.x - 1][self.agent.y]
        if self.agent.x == 0:
            possible_actions[Action.Left.value] = left.is_traversable
            if left.is_breakable:
                possible_actions[Action.BreakDoor.value] = True

        right = self.tiles[self.agent.x + 1][self.agent.y]
        if self.agent.x < GRID_SIZE - 1:
            possible_actions[Action.Right.value] = right.is_traversable
            if right.is_breakable:
                possible_actions[Action.BreakDoor.value] = True

        if right.is_breakable:
            possible_actions[Action.BreakDoor.value] = True

        top = self.tiles[self.agent.x][self.agent.y - 1]
        if self.agent.y > 0:
            possible_actions[Action.Up.value] = top.is_traversable
            if top.is_breakable:
                possible_actions[Action.BreakDoor.value] = True

        bottom = self.tiles[self.agent.x][self.agent.y + 1]
        if self.agent.y < GRID_SIZE - 1:
            possible_actions[Action.Down.value] = bottom.is_traversable
            if bottom.is_breakable:
                possible_actions[Action.BreakDoor.value] = True

        return possible_actions

    def draw(self, canvas):
        for row in self.tiles:
            for tile in row:
                tile.draw(canvas)

        self.target.draw(canvas)
        self.agent.draw(canvas)

    def random_empty_space(self):
        possible_tiles = []

        possible_tiles: list[Tile] = []
        for row in self.tiles:
            for tile in row:
                if (
                    isinstance(tile, Floor)
                    and not is_occupied(tile, self.target)
                    and not is_occupied(tile, self.agent)
                ):
                    possible_tiles.append(tile)

        if not possible_tiles:
            return None

        return np.random.choice(possible_tiles)
