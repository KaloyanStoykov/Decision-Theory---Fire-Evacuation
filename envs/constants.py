from q_learning.constants import RENDER
from enum import Enum
import numpy as np


class Config:
    def __init__(self):
        self.grid_size = 6
        self.window_size = 512
        self.fps = 10
        self.animation_delay = 1
        self.square_size = int(self.window_size / self.grid_size)
        self.durability_power = 1
        self.is_rendering = RENDER

        self.fire_size_on_object = 0.6
        self.chance_of_catching_fire = 0.04
        self.chance_of_self_extinguish = 0.004
        self.chance_of_wall_being_window = 0.1
        self.chance_of_wall_being_picture = 0.1
        self.random_target_location = True
        self.fire_state_count = 4

        self.min_reward = -100
        self.max_reward = 100
        self.time_step_punishment = -2
        self.death_punishment = -100
        self.illeagal_move_punishment = -5
        self.success_reward = 10
        self.distance_reward = 0.2  # lower this and increase time_step_punishment for more accurate results
        self.fire_extinguished_reward = 0
        self.max_distance = np.linalg.norm(
            np.array([0, 0]) - np.array([self.grid_size, self.grid_size])
        )

        self.evacuation_success_reward = 1000  # Reward for reaching the cat/target
        self.discount_factor = 0.9  # Discount factor for MDP Value Iteration

        # Static Fire switch
        self.static_fire_mode = True


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
    PUT_OUT_FIRE = 4  # This action should be included if your MDP considers it


type Observation = tuple[np.ndarray, np.ndarray]
