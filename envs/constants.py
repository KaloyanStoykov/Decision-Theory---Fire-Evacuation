from enum import Enum


class Config:
    def __init__(self):
        self.grid_size = 6
        self.window_size = 512
        self.fps = 100
        self.animation_delay = 1
        self.square_size = int(self.window_size / self.grid_size)
        self.durability_power = 1

        self.fire_size_on_object = 0.6
        self.chance_of_catching_fire = 0.04
        self.chance_of_self_extinguish = 0.004
        self.chance_of_wall_being_window = 0.1
        self.chance_of_wall_being_picture = 0.1

        self.initial_points = 1000
        self.item_damage_punishment = 10
        self.time_step_punishment = 1
        self.death_punishment = -10
        self.illeagal_move_punishment = -10


config = Config()


class Side(Enum):
    TOP = 0
    RIGHT = 1
    BOTTOM = 2
    LEFT = 3


class FloorPosition(Enum):
    TOP_LEFT = 0
    TOP_CENTER = 1
    TOP_RIGHT = 2
    MIDDLE_LEFT = 3
    MIDDLE_CENTER = 4
    MIDDLE_RIGHT = 5
    BOTTOM_LEFT = 6
    BOTTOM_CENTER = 7
    BOTTOM_RIGHT = 8


class FloorType(Enum):
    TILE = 0
    RED = 1
    BLUE = 2
    PURPLE = 3


class Items(Enum):
    WINDOW = 0
    RADIO = 1
    BOOKSHELF_EMPTY = 2
    BOOKSHELF_FULL = 3
    TABLE = 4
    TABLE_SMALL = 5
    CHAIR = 6
    CHAIR_RED = 7
    CHAIR_BLUE = 8
    CHAIR_PURPLE = 9
    OVEN = 10
    TOILET = 11
    POT = 12
    CHEST = 13
    STOOL = 14
    DOOR_OPEN = 15
    NIGHTSTAND = 16
    # DOOR = 17
    # TRAPDOOR = 18
    TRAPDOOR_OPEN = 19
    BIN = 20
    MODERN_BIN = 21
    PICTURE = 22
    POT_GREEN = 23
    POT_PINK = 24
    POT_RED = 25
    BED_RED = 26
    BED_BLUE = 27
    BED_PURPLE = 28


class Action(Enum):
    RIGHT = 0
    UP = 1
    LEFT = 2
    DOWN = 3
    PUT_OUT_FIRE = 4


type Observation = tuple[int, int]
