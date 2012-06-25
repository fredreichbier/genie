import struct
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from . import ImageAdapter

def _encode_pixel(color):
    """
        get the 4-byte RGBA representation of this color.
        *color* is either None (transparent) or a 3-tuple (R, G, B).
    """
    if color is None:
        return '\x00\x00\x00\x00'
    else:
        return struct.pack('=BBBB', color[0], color[1], color[2], 255)

class RawAdapter(ImageAdapter):
    """
        Write data as a stream of bytes in the "RGBA" format (one byte
        per component).
        Return it as a string.
    """
    def __init__(self, width, height):
        self.pixel_size = 4 # 4 bytes per pixel (RGBA)
        self.stride = width * self.pixel_size # this many pixels per row. yay.
        self.width, self.height = width, height
        self.array = bytearray(self.stride * height)

    def _get_byte_pos(self, x, y):
        return y * self.stride + x * self.pixel_size

    def draw_pixels(self, x, y, amount, color):
        pixel = _encode_pixel(color)
        for i in xrange(amount):
            pos = self._get_byte_pos(x + i, y)
            self.array[pos:pos + self.pixel_size] = pixel

    def get_image(self):
        return (self.width, self.height, self.array)
