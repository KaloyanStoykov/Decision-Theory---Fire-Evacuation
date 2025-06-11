from envs.constants import config


class Base:
    _image = None

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def _set_image(self, image):
        self._image = image

    def draw(self, canvas):
        canvas.blit(
            self._image, (self.x * config.square_size, self.y * config.square_size)
        )

    def update(self):
        pass

    def animate(self):
        pass
