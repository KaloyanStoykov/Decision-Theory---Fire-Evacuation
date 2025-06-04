from envs.sprites import sprite_map
from envs.constants import SQUARE_SIZE
from enum import Enum
import pygame

class State(Enum):
  Idle = 0
  Dying = 1

class FireFighter:
  def __init__(self, size):
    self.size = size
    self.anim_state = 0
    self.state = State.Idle
    self.update()
  
  def update(self):
    if self.state == State.Idle:
      self.anim_state = (self.anim_state + 1) % 6
      self.set_image(sprite_map["firefighter"]["idle"][self.anim_state])
    else:
      self.anim_state = (self.anim_state + 1) % 7
      self.set_image(sprite_map["firefighter"]["dying"][self.anim_state])

  def kill(self):
    self.state = State.Dying
    self.anim_state = 1

  def set_image(self, image):
    self._image = pygame.transform.scale(image, (self.size, self.size))

  def draw(self, canvas, x, y):
    self.update()
    canvas.blit(self._image, (x * self.size, y * self.size))
    