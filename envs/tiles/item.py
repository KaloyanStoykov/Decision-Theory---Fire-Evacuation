import pygame
from envs.tiles.floor import Floor
from envs.tiles.tile import Tile
from envs.constants import Items, config
from envs.ui.sprites import sprite_map


def durability_and_image_for_item(item_type: Items):
    match item_type:
        case Items.RADIO:
            return (9, sprite_map["radio"])
        case Items.BOOKSHELF_EMPTY:
            return (1, sprite_map["bookshelf"]["empty"])
        case Items.BOOKSHELF_FULL:
            return (1, sprite_map["bookshelf"]["full"])
        case Items.TABLE:
            return (1, sprite_map["table"]["big"])
        case Items.TABLE_SMALL:
            return (8, sprite_map["table"]["small"])
        case Items.CHAIR:
            return (6, sprite_map["chair"]["empty"])
        case Items.CHAIR_BLUE:
            return (6, sprite_map["chair"]["blue"])
        case Items.CHAIR_PURPLE:
            return (6, sprite_map["chair"]["purple"])
        case Items.CHAIR_RED:
            return (6, sprite_map["chair"]["red"])
        case Items.OVEN:
            return (1, sprite_map["oven"])
        case Items.TOILET:
            return (1, sprite_map["toilet"])
        case Items.POT:
            return (5, sprite_map["pot"]["empty"])
        case Items.POT_GREEN:
            return (5, sprite_map["pot"]["green"])
        case Items.POT_PINK:
            return (5, sprite_map["pot"]["pink"])
        case Items.POT_RED:
            return (5, sprite_map["pot"]["red"])
        case Items.CHEST:
            return (1, sprite_map["chest"])
        case Items.STOOL:
            return (4, sprite_map["stool"])
        case Items.BED_BLUE:
            return (1, sprite_map["bed"]["blue"])
        case Items.BED_RED:
            return (1, sprite_map["bed"]["red"])
        case Items.BED_PURPLE:
            return (1, sprite_map["bed"]["purple"])
        case Items.NIGHTSTAND:
            return (8, sprite_map["nightstand"])
        # case Items.DOOR:
        #     return (2, sprite_map["door"])
        # case Items.TRAPDOOR:
        #     return (1, sprite_map["trapdoor"]["closed"])
        case Items.DOOR_OPEN:
            return (2, sprite_map["door_open"])
        case Items.TRAPDOOR_OPEN:
            return (1, sprite_map["trapdoor"]["open"])
        case Items.BIN:
            return (7, sprite_map["bin"])
        case Items.MODERN_BIN:
            return (9, sprite_map["modern-bin"])
        case _:
            raise Exception(f"Item with type {item_type} not found")


# def is_door(item_type: Items):
#     return (
#         item_type == Items.DOOR
#         or item_type == Items.TRAPDOOR
#         or item_type == Items.TRAPDOOR_OPEN
#         or item_type == Items.DOOR_OPEN
#     )


class Item(Tile):
    is_destroyed = False

    def __init__(self, floor: Floor, type: Items):
        super().__init__(floor.x, floor.y)
        self._floor = floor
        # self.is_door = is_door(type)
        self.is_breakable = True
        # self.is_inflammable = True
        self.is_inflammable = False

        (durability, image) = durability_and_image_for_item(type)
        self.durability = durability * config.durability_power
        self._set_image(image)

    def damage(self):
        self.durability -= 1

        if self.durability == 0:
            self.is_destroyed = True

    def update(self):
        super().update()

        if self.is_on_fire and not config.static_fire_mode:
            self.damage()

            if self.is_destroyed:
                self._floor.set_on_fire()

    def draw(self, canvas):
        self._floor.draw(canvas)

        if not self.is_destroyed:
            super().draw(canvas)

    def draw_fire(self, canvas):
        scaled_sprite = pygame.transform.scale(
            sprite_map["fires"][self._fire_state - 1],
            (
                config.square_size * config.fire_size_on_object,
                config.square_size * config.fire_size_on_object,
            ),
        )
        canvas.blit(
            scaled_sprite,
            (
                self.x * config.square_size
                + config.square_size * (1 - config.fire_size_on_object) / 2,
                self.y * config.square_size
                + config.square_size * (1 - config.fire_size_on_object),
            ),
        )
