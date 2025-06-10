from envs.constants import SQUARE_SIZE


class Base:
    _image = None

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def _set_image(self, image):
        self._image = image

    def draw(self, canvas):
        canvas.blit(self._image, (self.x * SQUARE_SIZE, self.y * SQUARE_SIZE))

    def update(self):
        pass
