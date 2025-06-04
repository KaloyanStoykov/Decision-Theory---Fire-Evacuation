from envs.sprites import sprite_map
from envs.constants import SQUARE_SIZE
from enum import Enum
import pygame

PADDING = 16

class Cat:
  def __init__(self, size):
    self.size = size
    self.anim_state = 0
    self.update()
  
  def update(self):
    self.anim_state = (self.anim_state + 1) % 4
    self.set_image(sprite_map["cat"][self.anim_state])

  def set_image(self, image):
    self._image = pygame.transform.scale(image, (self.size - PADDING, self.size - PADDING))

  def draw(self, canvas, x, y):
    self.update()
    canvas.blit(self._image, (x * self.size + PADDING, y * self.size + PADDING))
    