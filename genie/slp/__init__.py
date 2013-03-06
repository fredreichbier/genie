"""
    A modular decoder for the SLP image format as used in the Genie engine.

    Thanks to http://alexander-jenkins.co.uk/blog/?p=9 and to
    http://www.digitization.org/wiki/index.php/SLP for the great documentation!
"""

import struct

import construct as cons

from .builtin_palettes import AOE2_PALETTE

class FrameAdapter(cons.Adapter):
    def _decode(self, obj, context):
        return Frame(obj)

FRAME = cons.Struct('frames',
    cons.ULInt32('cmd_table_offset'),
    cons.ULInt32('outline_table_offset'),
    cons.ULInt32('palette_offset'),
    cons.ULInt32('properties'),
    cons.SLInt32('width'),
    cons.SLInt32('height'),
    cons.SLInt32('hotspot_x'),
    cons.SLInt32('hotspot_y'),
)

HEADER = cons.Struct('header',
    cons.String('version', 4),
    cons.ULInt32('num_frames'),
    cons.String('comment', 24),
    cons.Array(lambda ctx: ctx['num_frames'], FrameAdapter(FRAME)),
)

class ImageAdapter(object):
    """
        A generic image writer. Could be used with PIL, cairo, ...
    """
    def __init__(self, frame):
        """
            Create a new image with the dimensions given by the frame object.
        """
        raise NotImplementedError()

    def draw_pixels(self, x, y, amount, color):
        """
            Draw *amount* pixels, horizontally, starting at *x*, *y*.
            *color* is a 3-tuple (R, G, B) or None for transparency.
        """
        raise NotImplementedError()

    def get_image(self):
        """
            Return the finished image object.
        """
        raise NotImplementedError()

class Frame(object):
    def __init__(self, structure):
        self.structure = structure
        self.width = self.structure.width
        self.height = self.structure.height
        self.hotspot_x = self.structure.hotspot_x
        self.hotspot_y = self.structure.hotspot_y
        self.slp_file = None # to be set later

    def parse_stream(self, stream, player=1, image_adapter_cls=None):
        """
            Use the image adapter class to create an image.
        """
        width, height = self.structure.width, self.structure.height
        if image_adapter_cls is None:
            image_adapter_cls = self.slp_file.image_adapter_cls
        adapter = image_adapter_cls(self)

        # First, the boundaries.
        stream.seek(self.structure.outline_table_offset)
        left_boundaries = []
        for y in xrange(height):
            left, right = struct.unpack('=HH', stream.read(4))
            if left == right == 0x8000:
                # fully transparent row
                adapter.draw_pixels(0, y, width, None)
                # this will tell the parser to skip this line later.
                left_boundaries.append(None)
            else:
                # draw transparent pixels.
                left_boundaries.append(left)
                adapter.draw_pixels(0, y, left, None)
                adapter.draw_pixels(width - right, y, right, None)

        # The command offsets.
        command_offsets = []
        for y in xrange(height):
            command_offsets.append(struct.unpack('=I', stream.read(4))[0])

        # Now, the actual commands.
        stream.seek(command_offsets[0])
        x = left_boundaries[0]
        y = 0

        while x is None:
            # maybe the first row is transparent already?
            y += 1
            x = left_boundaries[y]

        def _get_byte():
            """ take a byte from the stream. """
            return struct.unpack('=B', stream.read(1))[0]

        def _get_4ornext(opcode):
            """
                either return the 4 most significant bits from the opcode
                or the complete next byte if the former is 0.
            """
            return (opcode >> 4) or _get_byte()

        def _get_bigbig(opcode):
            """ right-shift 4 bits to the right + next byte """
            return ((opcode & 0xf0) << 4) + _get_byte()

        def _draw_pixels(amount, palette_index):
            assert x + amount <= width
            if palette_index is None:
                color = None
            else:
                color = self.slp_file.palette[palette_index]
            adapter.draw_pixels(x, y, amount, color)

        def _get_palette_index(player, relindex):
            return player * 16 + relindex

        while y < height:
            opcode = _get_byte()
            twobit = opcode & 0b11
            fourbit = opcode & 0b1111

            if x > width:
                raise Exception('%d > %d' % (x, width))

            if fourbit == 0x0f:
                y += 1
                if y < height:
                    x = left_boundaries[y]
                    while x is None:
                        # fully transparent line! (skip this line)
                        y += 1
                        x = left_boundaries[y]
                    if stream.tell() != command_offsets[y]:
                        raise Exception('%d but should be %d' % (stream.tell(), command_offsets[y]))
            elif fourbit == 0x06:
                # player colors
                amount = _get_4ornext(opcode)
                #print 'player colors', amount
                for _ in xrange(amount):
                     relindex = _get_byte()
                     _draw_pixels(1, _get_palette_index(player, relindex))
                     x += 1
            elif fourbit == 0x0e:
                # Extended command (shadows etc.)
                # get the high 4 bits for the extended command
                # I only found information about this opcode in
                # the slp.rtf file (see README).
                # For now, this doesn't actually do anything apart
                # from reading the correct number of bytes from the
                # stream to parse the image data correctly.
                extended = opcode >> 4
                if extended == 0:
                    # woho! this should only be drawn if the
                    # sprite is not x-flipped. TODO.
                    pass
                elif extended == 1:
                    # this should only be drawn if the sprite
                    # is x-flipped. TODO.
                    pass
                elif extended in (2, 3):
                    # do some fiddling with transform color tables.
                    # see documentation.
                    pass
                elif extended in (4, 6):
                    # special color 1/2, but only 1 byte.
                    pass
                elif extended in (5, 7):
                    # special color 1/2, read amount from stream.
                    amount = _get_byte()
                else:
                    raise NotImplementedError('Unknown extended opcode: %r' % extended)
            elif fourbit == 0x07:
                # fill
                amount = _get_4ornext(opcode)
                #print 'fill', amount
                palette_index = _get_byte()
                _draw_pixels(amount, palette_index)
                x += amount
            elif fourbit == 0x0a:
                amount = _get_4ornext(opcode)
                #print 'player fill', amount
                _draw_pixels(amount, _get_palette_index(player, _get_byte()))
                x += amount
            elif fourbit in (0x4e, 0x5e, 0x0b):
                raise NotImplementedError('The 0x%x opcode is not yet implemented.' % fourbit)
            elif twobit == 0:
                # draw
                amount = opcode >> 2
                #print 'draw', amount
                for _ in xrange(amount):
                    _draw_pixels(1, _get_byte())
                    x += 1
            elif twobit == 1:
                # skip pixels
                # 2ornext
                amount = opcode >> 2
                #print 'skip', amount
                if amount == 0:
                    amount = _get_byte()
                _draw_pixels(amount, None)
                x += amount
            elif twobit == 2:
                amount = _get_bigbig(opcode)
                #print 'big draw', amount
                for _ in xrange(amount):
                    _draw_pixels(1, _get_byte())
                    x += 1
            elif twobit == 3:
                amount = _get_bigbig(opcode)
                #print 'big skip', amount
                _draw_pixels(amount, None)
                x += amount
            else:
                raise Exception()

        return adapter.get_image()

class SLPFile(object):
    """
        A SLP file containing multiple `Frame` objects. You need to specify
        an `ImageAdapter` subclass (or factory function) to build images, also,
        a palette dictionary (AOE1 is the default).
    """
    def __init__(self, image_adapter_cls, stream=None, palette=AOE2_PALETTE):
        self.header = None
        self.image_adapter_cls = image_adapter_cls
        self.palette = palette
        if stream is not None:
            self.parse_stream(stream)

    def parse_stream(self, stream):
        self.header = HEADER.parse_stream(stream)
        for frame in self.header.frames:
            frame.slp_file = self # TODO: not so nice
        self.frames = self.header.frames

