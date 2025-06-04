import pygame
from envs.sprites import sprite_map
from envs.constants import FIRE_LAST_STEP

class Tile:
  is_on_fire = False
  _image = None
  _fire_state = 1
  
  def __init__(self, is_traversable, inflammable):
    self.is_traversable = is_traversable
    self.is_inflammable = inflammable
  
  def set_image(self, image, size):
    self._image = pygame.transform.scale(image, (size, size))
  
  def increase_fire(self):
    self._fire_state += 1
    
    if self._fire_state > FIRE_LAST_STEP:
      self._fire_state= 1
  
  def set_on_fire(self):
    if not self.is_inflammable:
      raise Exception("Tile is not inflammable")
    
    self.is_on_fire = True
        
  def put_out_fire(self):
    self.is_on_fire = False
    self._fire_state = 1
  
  def draw(self, canvas, square_size, x, y):
    canvas.blit(self._image, (x * square_size, y * square_size))
    
    if self.is_on_fire:
      self.draw_fire(canvas, square_size, x, y)

  def draw_fire(self, canvas, square_size, x, y):
    scaled_sprite = pygame.transform.scale(sprite_map["fires"][self._fire_state - 1], (square_size, square_size))
    canvas.blit(scaled_sprite, (x * square_size, y * square_size))
    self.increase_fire()