from envs.constants import Action
import pygame
from envs.ui.sprites import sprite_map
import asyncio
from envs.constants import config
import numpy as np
import math

GREEN = GREEN = (100, 255, 100)
RED = (255, 60, 60)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)


class Window:
    def __init__(self):
        pygame.init()
        pygame.display.init()

        self.controlls = {
            "w": {"pos": [1, 4], "action": Action.UP},
            "a": {"pos": [0, 5], "action": Action.LEFT},
            "s": {"pos": [0, 4], "action": Action.DOWN},
            "d": {"pos": [0, 3], "action": Action.RIGHT},
            "u": {"pos": [1, 1], "action": Action.UP},
            "l": {"pos": [0, 2], "action": Action.LEFT},
            "down": {"pos": [0, 1], "action": Action.DOWN},
            "r": {"pos": [0, 0], "action": Action.RIGHT},
            "space": {"pos": [1, 3], "action": Action.PUT_OUT_FIRE},
        }

        self.controllBtnSize = 22

        for controll in self.controlls.keys():
            if controll == "space":
                self.controlls[controll]["btn"] = pygame.Rect(
                    0, 0, self.controllBtnSize, self.controllBtnSize
                )
                self.controlls[controll]["btn"].center = (
                    config.window_size
                    - (self.controlls[controll]["pos"][1] + 1) * self.controllBtnSize
                    + 2,
                    config.window_size
                    - (self.controlls[controll]["pos"][0] + 1) * self.controllBtnSize,
                )

            else:
                self.controlls[controll]["btn"] = pygame.Rect(
                    0, 0, self.controllBtnSize, self.controllBtnSize
                )
                self.controlls[controll]["btn"].center = (
                    config.window_size
                    - (self.controlls[controll]["pos"][1] + 1) * self.controllBtnSize,
                    config.window_size
                    - (self.controlls[controll]["pos"][0] + 1) * self.controllBtnSize,
                )

        try:
            self._font = pygame.font.Font("assets/PressStart2P-Regular.ttf", 32)
            self._small_font = pygame.font.Font("assets/PressStart2P-Regular.ttf", 20)
            self._extra_small_font = pygame.font.Font(
                "assets/PressStart2P-Regular.ttf", 12
            )
            self._extra_extra_small_font = pygame.font.Font(
                "assets/PressStart2P-Regular.ttf", 8
            )
        except:
            self._font = pygame.font.SysFont("Courier", 32)
            self._small_font = pygame.font.SysFont("Courier", 20)
            self._extra_small_font = pygame.font.SysFont("Courier", 12)
            self._extra_extra_small_font = pygame.font.SysFont("Courier", 8)

        self._canvas = pygame.Surface((config.window_size, config.window_size))
        self._canvas.fill((255, 255, 255))
        self._screen = pygame.display.set_mode((config.window_size, config.window_size))
        self._clock = pygame.time.Clock()
        self._animation_stage = 0

    def draw(self, draw_func, animate_func):
        if self._animation_stage >= config.fps * config.animation_delay:
            animate_func()
            self._animation_stage = 0
        else:
            self._animation_stage += config.fps

        draw_func(self._canvas)

        self._screen.blit(self._canvas, self._canvas.get_rect())
        self.draw_controlls()

        pygame.event.pump()
        pygame.display.update()
        self._clock.tick(config.fps)

    def draw_controlls(self):
        for controll in self.controlls.keys():
            if controll == "space":
                self._screen.blit(
                    sprite_map["controlls"][controll],
                    self.controlls[controll]["btn"].topleft,
                )

                text = self._extra_extra_small_font.render("Space", True, BLACK)
                self._screen.blit(
                    text,
                    text.get_rect(
                        center=(
                            config.window_size
                            - self.controlls[controll]["pos"][1] * self.controllBtnSize
                            - 10,
                            config.window_size
                            - self.controlls[controll]["pos"][1] * self.controllBtnSize
                            + 20,
                        )
                    ),
                )

            else:
                self._screen.blit(
                    sprite_map["controlls"][controll],
                    self.controlls[controll]["btn"].topleft,
                )

        pygame.display.flip()

    def close(self):
        if self._screen is not None:
            pygame.display.quit()
            pygame.quit()

    async def game_over_screen(self):
        self._draw_game_over()
        while True:
            await asyncio.sleep(0)

            for event in pygame.event.get():
                match event.type:
                    case pygame.QUIT:
                        return False
                    case pygame.KEYDOWN:
                        if (
                            event.key == pygame.K_ESCAPE
                            or event.key == pygame.K_q
                            or event.key == pygame.K_n
                        ):
                            return False

                        elif (
                            event.key == pygame.K_KP_ENTER
                            or event.key == pygame.K_RETURN
                            or event.key == pygame.K_y
                        ):
                            return True
                    case pygame.MOUSEBUTTONDOWN:
                        if self._yes_rect.collidepoint(event.pos):
                            return True
                        elif self._no_rect.collidepoint(event.pos):
                            return False

                    case pygame.MOUSEMOTION:
                        mouse_pos = pygame.mouse.get_pos()
                        hover_yes = self._yes_rect.collidepoint(mouse_pos)
                        hover_no = self._no_rect.collidepoint(mouse_pos)

                        self._screen.blit(self._canvas, self._canvas.get_rect())
                        self._draw_game_over(hover_yes, hover_no)

            self._clock.tick(config.fps)

    def _draw_game_over(self, hover_yes=False, hover_no=False):
        dim_overlay = pygame.Surface((config.window_size, config.window_size))
        dim_overlay.set_alpha(180)
        dim_overlay.fill(BLACK)
        self._screen.blit(dim_overlay, (0, 0))

        self._center = config.window_size // 2

        # Game Over text
        text = self._font.render("Game Over", True, RED)
        text_rect = text.get_rect(center=(self._center, self._center - 60))
        self._screen.blit(text, text_rect)

        self._draw_yes_no_buttons(hover_yes, hover_no)
        pygame.display.flip()

    def _draw_yes_no_buttons(self, hover_yes, hover_no):
        continue_text = self._extra_small_font.render("Continue?", True, WHITE)
        self._screen.blit(
            continue_text,
            continue_text.get_rect(center=(self._center, self._center - 20)),
        )

        spacing = 80
        button_size = (70, 30)
        self._yes_rect = pygame.Rect(0, 0, *button_size)
        self._no_rect = pygame.Rect(0, 0, *button_size)
        self._yes_rect.center = (self._center - spacing // 2, self._center + 30)
        self._no_rect.center = (self._center + spacing // 2, self._center + 30)

        if hover_yes:
            pygame.draw.rect(self._screen, GREEN, self._yes_rect)
        else:
            pygame.draw.rect(self._screen, GREEN, self._yes_rect, width=2)

        if hover_no:
            pygame.draw.rect(self._screen, RED, self._no_rect)
        else:
            pygame.draw.rect(self._screen, RED, self._no_rect, width=2)

        # Render "Yes" with underlined Y
        y_text = self._extra_small_font.render("Y", True, BLACK if hover_yes else GREEN)
        y_pos = y_text.get_rect(
            center=(self._yes_rect.centerx - 10, self._yes_rect.centery)
        )
        es_text = self._extra_small_font.render(
            "es", True, BLACK if hover_yes else GREEN
        )
        es_pos = es_text.get_rect(
            center=(self._yes_rect.centerx + 8, self._yes_rect.centery)
        )
        underline_y = pygame.Rect(y_pos.left, y_pos.bottom + 1, y_pos.width, 2)

        self._screen.blit(y_text, y_pos)
        self._screen.blit(es_text, es_pos)
        pygame.draw.rect(self._screen, BLACK if hover_yes else GREEN, underline_y)

        n_text = self._extra_small_font.render("N", True, BLACK if hover_no else RED)
        n_pos = n_text.get_rect(
            center=(self._no_rect.centerx - 6, self._no_rect.centery)
        )
        o_text = self._extra_small_font.render("o", True, BLACK if hover_no else RED)
        o_pos = o_text.get_rect(
            midleft=(self._no_rect.centerx + 4, self._no_rect.centery)
        )
        underline_n = pygame.Rect(n_pos.left, n_pos.bottom + 1, n_pos.width, 2)

        self._screen.blit(o_text, o_pos)
        self._screen.blit(n_text, n_pos)
        pygame.draw.rect(self._screen, BLACK if hover_no else RED, underline_n)

    async def win_screen(self):
        confetti_list = [ConfettiParticle() for _ in range(150)]
        self._draw_congrats(confetti_list)

        while True:
            await asyncio.sleep(0)

            for c in confetti_list:
                c.update()

            mouse_pos = pygame.mouse.get_pos()
            hover_yes = self._yes_rect.collidepoint(mouse_pos)
            hover_no = self._no_rect.collidepoint(mouse_pos)
            self._screen.blit(self._canvas, self._canvas.get_rect())
            self._draw_congrats(confetti_list, hover_yes, hover_no)

            for event in pygame.event.get():
                match event.type:
                    case pygame.QUIT:
                        return False
                    case pygame.KEYDOWN:
                        if (
                            event.key == pygame.K_ESCAPE
                            or event.key == pygame.K_q
                            or event.key == pygame.K_n
                        ):
                            return False

                        elif (
                            event.key == pygame.K_KP_ENTER
                            or event.key == pygame.K_RETURN
                            or event.key == pygame.K_y
                        ):
                            return True
                    case pygame.MOUSEBUTTONDOWN:
                        if self._yes_rect.collidepoint(event.pos):
                            return True
                        elif self._no_rect.collidepoint(event.pos):
                            return False

            self._clock.tick(config.fps)

    def _draw_congrats(self, confetti, hover_yes=False, hover_no=False):
        dim_overlay = pygame.Surface((config.window_size, config.window_size))
        dim_overlay.set_alpha(180)
        dim_overlay.fill(BLACK)
        self._screen.blit(dim_overlay, (0, 0))

        self._center = config.window_size // 2

        text = self._font.render("Congrats!!", True, GREEN)
        text_rect = text.get_rect(center=(self._center, self._center - 60))
        self._screen.blit(text, text_rect)

        self._draw_yes_no_buttons(hover_yes, hover_no)

        for c in confetti:
            c.draw(self._screen)

        pygame.display.flip()


class ConfettiParticle:
    def __init__(self):
        self.x = np.random.uniform(0, config.window_size)
        self.y = np.random.uniform(-100, -10)
        self.size = np.random.randint(4, 7)
        colors = ((255, 0, 0), (0, 255, 0), (0, 150, 255), (255, 255, 0), (255, 0, 255))

        self.color = colors[np.random.randint(0, 5)]
        self.speed_y = np.random.uniform(1, 4)
        self.drift = np.random.uniform(-1.5, 1.5)
        self.angle = np.random.uniform(0, 360)
        self.spin = np.random.uniform(-5, 5)

    def update(self):
        self.y += self.speed_y
        self.x += self.drift
        self.angle = (self.angle + self.spin) % 360

        if self.y > config.window_size:
            self.y = 0

    def draw(self, surface):
        s = self.size
        points = [
            (
                self.x + s * math.cos(math.radians(self.angle)),
                self.y + s * math.sin(math.radians(self.angle)),
            ),
            (
                self.x - s * math.cos(math.radians(self.angle)),
                self.y + s * math.sin(math.radians(self.angle)),
            ),
            (
                self.x - s * math.cos(math.radians(self.angle)),
                self.y - s * math.sin(math.radians(self.angle)),
            ),
            (
                self.x + s * math.cos(math.radians(self.angle)),
                self.y - s * math.sin(math.radians(self.angle)),
            ),
        ]
        pygame.draw.polygon(surface, self.color, points)
