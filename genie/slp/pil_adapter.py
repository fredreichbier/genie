from PIL import Image, ImageDraw

from . import ImageAdapter

class PILAdapter(ImageAdapter):
    def __init__(self, frame):
        self.image = Image.new('RGBA', (frame.width, frame.height), (255, 255, 255, 255))
        self.draw = ImageDraw.ImageDraw(self.image)

    def draw_pixels(self, x, y, amount, color):
        if color is None:
            color = (255, 255, 255, 0)
        else:
            color += (255,)
        if amount == 1:
            self.draw.point((x, y), fill=color)
        else:
            self.draw.line((x, y, x + amount, y), fill=color)

    def get_image(self):
        return self.image
