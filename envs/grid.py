import numpy as np
from envs.constants import FloorType, config
from envs.tiles.tile import Tile
from envs.tiles.wall import Wall
from envs.tiles.item import Item, Items
from envs.tiles.floor import Floor
from envs.utilities import decide_action, random_tile, is_occupied
from envs.characters.cat import Cat
from envs.characters.firefighter import FireFighter
from envs.constants import Action
from envs.ui.sprites import sprite_map
from envs.ui.room import RoomFactory
from envs.utilities import out_of_grid

ACTION_TO_DIRECTION = {
    Action.RIGHT: np.array([1, 0]),
    Action.UP: np.array([0, -1]),
    Action.LEFT: np.array([-1, 0]),
    Action.DOWN: np.array([0, 1]),
    Action.PUT_OUT_FIRE: np.array([0, 0]),
}


class Grid:
    target: Cat = None
    agent: FireFighter = None

    def __init__(
        self,
        room_factory: RoomFactory,
        static_mode=False,
        initial_agent_pos=None,
        initial_target_pos=None,
        np_random=None,
    ):
        self.np = np_random if np_random is not None else np.random
        self.room_factory = room_factory
        self.is_animation_on_going = False
        self.extinguishing_tile = None
        self.extinguishing_state = 0
        self.static_mode = static_mode
        self.initial_agent_pos = initial_agent_pos
        self.initial_target_pos = initial_target_pos
        self.create_grid()

    def create_grid(self):
        self.tiles: list[list[Tile]] = [
            [None for _ in range(config.grid_size)] for _ in range(config.grid_size)
        ]

        self.room_factory.create_walls(self)
        self.room_factory.lay_floors(self)
        self.room_factory.create_items(self)

        free_tiles: list[Tile] = list(
            filter(
                lambda tile: tile.is_traversable and not tile.is_on_fire,
                [tile for row in self.tiles for tile in row],
            )
        )

        target_location = (
            self.np.choice(free_tiles)
            if config.random_target_location
            else free_tiles[0]
        )

        free_tiles.remove(target_location)
        self.target = Cat(np.array([target_location.x, target_location.y]))
        agent_location: Tile = self.np.choice(free_tiles)
        self.agent = FireFighter(np.array([agent_location.x, agent_location.y]))

    def is_agent_dead(self):
        return self.tiles[self.agent.x][self.agent.y].is_on_fire

    def is_cat_rescued(self):
        return np.array_equal(self.agent.location, self.target.location)

    def update(self, action: Action = None):
        if action is None:
            self._update_tiles()
            return False

        is_legal_move = True
        next_agent_location = self.agent.location + ACTION_TO_DIRECTION[action]

        if (
            out_of_grid(next_agent_location)
            or not self._tile_at(next_agent_location).is_traversable
        ):
            self._update_tiles()
            return False

        self.agent.move(next_agent_location)

        if action == Action.PUT_OUT_FIRE:
            is_legal_move = False
            for movement in [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT]:
                border_tile_location = (
                    self.agent.location + ACTION_TO_DIRECTION[movement]
                )

                if (
                    not out_of_grid(border_tile_location)
                    and self._tile_at(border_tile_location).is_on_fire
                ):
                    self.extinguishing_tile = self._tile_at(border_tile_location)
                    self.extinguishing_tile.put_out_fire()
                    is_legal_move = True
                    break
        elif self.is_agent_dead():
            if self.is_animation_on_going:
                self.is_animation_on_going = self.agent._anim_state != 0
            else:
                self.agent.kill()
                self.is_animation_on_going = True

        self._update_tiles()

        return is_legal_move

    def _update_tiles(self):
        if config.static_fire_mode:
            return

        for row in self.tiles:
            for tile in row:
                tile.update()

        if decide_action(config.chance_of_catching_fire):
            tile = random_tile(self.tiles, self.target, self.agent, inflammable=True)
            if tile:
                tile.set_on_fire()
        if decide_action(config.chance_of_self_extinguish):
            tile = random_tile(self.tiles, self.target, self.agent, burning=True)
            if tile:
                tile.put_out_fire()

    def draw(self, canvas):
        for row in self.tiles:
            for tile in row:
                tile.draw(canvas)

        self.target.draw(canvas)
        self.agent.draw(canvas)

        if self.extinguishing_tile is not None:
            self.extinguishing_tile.is_on_fire = True
            self.extinguishing_tile.draw(canvas)
            self.extinguishing_tile.is_on_fire = False
            if self.extinguishing_state < 2:
                canvas.blit(
                    sprite_map["firefighter"]["put_out_fire"][self.extinguishing_state],
                    (
                        self.extinguishing_tile.x * config.square_size,
                        self.extinguishing_tile.y * config.square_size,
                    ),
                )
            else:
                self.extinguishing_tile = None
                self.extinguishing_state = 0
                self.is_animation_on_going = False

        if self.is_animation_on_going and self.agent._anim_state == 0:
            self.is_animation_on_going = False

    def animate(self):
        for row in self.tiles:
            for tile in row:
                tile.animate()

        self.target.animate()
        self.agent.animate()

        if self.extinguishing_tile is not None:
            if self.extinguishing_state < 2:
                self.extinguishing_state += 1

    def _random_empty_space(self):
        possible_tiles = []

        possible_tiles: list[Tile] = []
        for row in self.tiles:
            for tile in row:
                if (
                    isinstance(tile, Floor)
                    and (self.target is None or not is_occupied(tile, self.target))
                    and (self.agent is None or not is_occupied(tile, self.agent))
                ):
                    possible_tiles.append(tile)

        if not possible_tiles:
            return None

        return np.random.choice(possible_tiles)

    def _tile_at(self, pos: tuple[int]):
        return self.tiles[pos[0]][pos[1]]
