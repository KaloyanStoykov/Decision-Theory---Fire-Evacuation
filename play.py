import pygame
import numpy as np
from envs.constants import Action, config
from envs.ui.window import Window
from envs.grid import Grid
import threading
from time import sleep


config.fps = 8
window = Window()
grid = Grid()
pressed_keys = pygame.key.get_pressed()
running = True

pygame.key.set_repeat(400, 170)


def detect_input():
    global pressed_keys, running
    while running:
        pressed_keys = pygame.key.get_pressed()
        sleep(0.001)


def play():
    global running
    thread = threading.Thread(target=detect_input, daemon=True)
    thread.start()

    while running:
        action = None

        if pressed_keys[pygame.K_UP]:
            action = Action.UP
        elif pressed_keys[pygame.K_DOWN]:
            action = Action.DOWN
        elif pressed_keys[pygame.K_LEFT]:
            action = Action.LEFT
        elif pressed_keys[pygame.K_RIGHT]:
            action = Action.RIGHT
        elif pressed_keys[pygame.K_KP_ENTER]:
            action = Action.PUT_OUT_FIRE
        elif pressed_keys[pygame.K_ESCAPE] or pressed_keys[pygame.K_q]:
            running = False

        if action:
            grid.update(action)

        if np.array_equal(grid.agent.location, grid.target.location):
            running = False

        if grid.is_agent_dead():
            while grid.agent._anim_state != 0:
                window.draw(lambda canvas: grid.draw(canvas))

            grid.create_grid()
        else:
            window.draw(lambda canvas: grid.draw(canvas))

    window.close()


if __name__ == "__main__":
    play()
