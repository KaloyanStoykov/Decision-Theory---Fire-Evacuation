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

ACTION_TO_DIRECTION = {
    Action.RIGHT.value: np.array([1, 0]),
    Action.UP.value: np.array([0, -1]),
    Action.LEFT.value: np.array([-1, 0]),
    Action.DOWN.value: np.array([0, 1]),
    Action.PUT_OUT_FIRE.value: np.array([0, 0]),
}


class Grid:
    def __init__(self, np_random=np.random, static_mode=False, initial_agent_pos=None, initial_target_pos=None):
        self.np = np_random
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

        self._create_walls()
        self._lay_floors()
        self._create_items()

        free_tiles: list[Tile] = list(
            filter(
                lambda tile: tile.is_traversable,
                [tile for row in self.tiles for tile in row],
            )
        )

        # Handle target and agent placement based on mode
        # The fix is here: check if initial_agent_pos is not None
        if self.static_mode and self.initial_agent_pos is not None and self.initial_target_pos is not None: # Fix applied here
            agent_location_xy = self.initial_agent_pos
            target_location_xy = self.initial_target_pos
        else:
            # Dynamic placement for Q-learning or if initial positions aren't provided
            if free_tiles: # Ensure there are free tiles
                # Make sure agent and target don't start on the same tile
                if len(free_tiles) < 2: # Not enough space for distinct agent/target
                    print("Warning: Not enough free tiles to place agent and target distinctly.")
                    # Handle this edge case, maybe place them on the same tile for now
                    target_tile = self.np.choice(free_tiles)
                    agent_tile = target_tile
                else:
                    target_tile = self.np.choice(free_tiles)
                    free_tiles.remove(target_tile)
                    agent_tile = self.np.choice(free_tiles)
                
                target_location_xy = np.array([target_tile.x, target_tile.y])
                agent_location_xy = np.array([agent_tile.x, agent_tile.y])
            else:
                raise ValueError("No traversable tiles available to place agent or target.")


        self.target = Cat(target_location_xy)
        self.agent = FireFighter(agent_location_xy)

        # For static mode, ensure fire is set up consistently if required by MDP
        # Currently, the MDP assumes a static *fire environment* but doesn't explicitly
        # set fire on tiles in the template grid. If you want static fire *on* certain tiles,
        # you would add that logic here based on self.static_mode and a predefined list.
        # For now, chance_of_catching_fire is handled externally.

    def _create_walls(self):
        # Keep walls static and predetermined
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
            self.tiles[pos[0]][pos[1]] = Wall(pos[0], pos[1])

        for pos in positions:
            self.tiles[pos[0]][pos[1]].register_neighbors(self.tiles)

    def _lay_floors(self):
        for x in range(config.grid_size):
            for y in range(config.grid_size):
                if not self.tiles[x][y]:
                    self.tiles[x][y] = Floor(
                        x,
                        y,
                        self.tiles,
                        FloorType.BLUE,
                    )

    def _create_items(self):
        # Keep items static and predetermined
        self.tiles[0][3] = Item(self.tiles[0][3], Items.BOOKSHELF_FULL)
        self.tiles[1][0] = Item(self.tiles[1][0], Items.BED_RED)
        self.tiles[2][0] = Item(self.tiles[2][0], Items.POT_GREEN)

    def is_agent_dead(self):
        return self.tiles[self.agent.x][self.agent.y].is_on_fire

    def update(self, action: Action = None):
        if action is not None:
            next_agent_location = (
                self.agent.location + ACTION_TO_DIRECTION[action.value]
            )

            if (
                next_agent_location[0] < 0
                or next_agent_location[1] < 0
                or next_agent_location[0] >= config.grid_size
                or next_agent_location[1] >= config.grid_size
                or not self.tiles[next_agent_location[0]][
                    next_agent_location[1]
                ].is_traversable
            ):
                # If static_mode is True, fire and self-extinguish chances should be skipped
                if not self.static_mode:
                    self._update_tiles()
                    if decide_action(config.chance_of_catching_fire):
                        tile = random_tile(self.tiles, self.target, self.agent, inflammable=True)
                        if tile:
                            tile.set_on_fire()
                    if decide_action(config.chance_of_self_extinguish):
                        tile = random_tile(self.tiles, self.target, self.agent, burning=True)
                        if tile:
                            tile.put_out_fire()
                return False

            self.agent.move(next_agent_location)

            if action == Action.PUT_OUT_FIRE:
                for movement in [Action.UP, Action.DOWN, Action.LEFT, Action.RIGHT]:
                    border_tile_location = (
                        self.agent.location + ACTION_TO_DIRECTION[movement.value]
                    )

                    if (
                        border_tile_location[0] < 0
                        or border_tile_location[1] < 0
                        or border_tile_location[0] >= config.grid_size
                        or border_tile_location[1] >= config.grid_size
                        or not self.tiles[border_tile_location[0]][
                            border_tile_location[1]
                        ].is_inflammable
                    ):
                        continue

                    if self.tiles[border_tile_location[0]][
                        border_tile_location[1]
                    ].is_on_fire:
                        self.extinguishing_tile = self.tiles[border_tile_location[0]][
                            border_tile_location[1]
                        ]
                        break

            if self.is_agent_dead():
                if self.is_animation_on_going:
                    self.is_animation_on_going = self.agent._anim_state != 0
                else:
                    self.agent.kill()
                    self.is_animation_on_going = True

        # Only update tiles for dynamic fire, not for static mode
        if not self.static_mode:
            self._update_tiles()

            if decide_action(config.chance_of_catching_fire):
                tile = random_tile(self.tiles, self.target, self.agent, inflammable=True)
                if tile:
                    tile.set_on_fire()

            if decide_action(config.chance_of_self_extinguish):
                tile = random_tile(self.tiles, self.target, self.agent, burning=True)
                if tile:
                    tile.put_out_fire()

        return True

    def _update_tiles(self):
        for row in self.tiles:
            for tile in row:
                tile.update()

    def draw(self, canvas):
        for row in self.tiles:
            for tile in row:
                tile.draw(canvas)

        self.target.draw(canvas)
        self.agent.draw(canvas)

        if self.extinguishing_tile is not None:
            self.extinguishing_tile.draw(canvas)
            if self.extinguishing_state < 2:
                canvas.blit(
                    sprite_map["firefighter"]["put_out_fire"][self.extinguishing_state],
                    (
                        self.extinguishing_tile.x * config.square_size,
                        self.extinguishing_tile.y * config.square_size,
                    ),
                )
            else:
                self.extinguishing_tile.put_out_fire()
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
                    and not is_occupied(tile, self.target)
                    and not is_occupied(tile, self.agent)
                ):
                    possible_tiles.append(tile)

        if not possible_tiles:
            return None

        return np.random.choice(possible_tiles)