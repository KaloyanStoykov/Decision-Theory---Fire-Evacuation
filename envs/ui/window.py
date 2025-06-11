import pygame
from envs.constants import config


class Window:
    def __init__(self):
        pygame.init()
        pygame.display.init()

        self._canvas = pygame.Surface((config.window_size, config.window_size))
        self._canvas.fill((255, 255, 255))
        self._window = pygame.display.set_mode((config.window_size, config.window_size))
        self._clock = pygame.time.Clock()

    def draw(self, draw_func):
        draw_func(self._canvas)
        self._window.blit(self._canvas, self._canvas.get_rect())

        pygame.event.pump()
        pygame.display.update()
        self._clock.tick(config.fps)

    def close(self):
        if self._window is not None:
            pygame.display.quit()
            pygame.quit()
