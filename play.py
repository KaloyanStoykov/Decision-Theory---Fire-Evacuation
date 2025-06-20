import asyncio


import pygame
import numpy as np
from envs.constants import Action, config
from envs.ui.window import Window
from envs.grid import Grid
from envs.ui.sprites import load_srpite_map
from envs.ui.play_room import PlayRoom
import sys
import asyncio

config.grid_size = 8
config.window_size = 512
config.square_size = int(config.window_size / config.grid_size)
config.fps = 60
config.animation_delay = 60 / 8
config.static_fire_mode = False
config.chance_of_catching_fire = 0.03
config.chance_of_self_extinguish = config.chance_of_catching_fire / 15

load_srpite_map()
window = Window()
grid = Grid(PlayRoom())


async def play():
    running = True

    while running:
        if sys.platform == "emscripten":
            await asyncio.sleep(0)

        action = None

        for event in pygame.event.get():
            match event.type:
                case pygame.QUIT:
                    running = False
                case pygame.MOUSEBUTTONDOWN:
                    for controll in window.controlls.keys():
                        if window.controlls[controll]["btn"].collidepoint(event.pos):
                            match controll:
                                case "w" | "u":
                                    action = Action.UP
                                case "s" | "down":
                                    action = Action.DOWN
                                case "a" | "l":
                                    action = Action.LEFT
                                case "d" | "r":
                                    action = Action.RIGHT
                                case "space":
                                    action = Action.PUT_OUT_FIRE
                case pygame.KEYDOWN:
                    match event.key:
                        case pygame.K_UP | pygame.K_w:
                            action = Action.UP
                        case pygame.K_DOWN | pygame.K_s:
                            action = Action.DOWN
                        case pygame.K_LEFT | pygame.K_a:
                            action = Action.LEFT
                        case pygame.K_RIGHT | pygame.K_d:
                            action = Action.RIGHT
                        case pygame.K_KP_ENTER | pygame.K_RETURN | pygame.K_SPACE:
                            action = Action.PUT_OUT_FIRE
                        case pygame.K_ESCAPE | pygame.K_q | pygame.K_SPACE:
                            running = False

        grid.update(action)

        if grid.is_cat_rescued():
            window.draw(lambda canvas: grid.draw(canvas), lambda: grid.animate())
            running = await window.win_screen()
            if running:
                grid.create_grid()

        if grid.is_agent_dead():
            while grid.is_animation_on_going:
                await asyncio.sleep(0)
                window.draw(lambda canvas: grid.draw(canvas), lambda: grid.animate())

            running = await window.game_over_screen()

            if running:
                grid.create_grid()
        else:
            window.draw(lambda canvas: grid.draw(canvas), lambda: grid.animate())

    window.close()


asyncio.run(play())
