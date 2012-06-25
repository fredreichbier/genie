import struct

import construct as cons

#per_frame = cons.Struct('per_frame',

frame = cons.Struct('frames',
    cons.ULInt32('cmd_table_offset'),
    cons.ULInt32('outline_table_offset'),
    cons.ULInt32('palette_offset'),
    cons.ULInt32('properties'),
    cons.SLInt32('width'),
    cons.SLInt32('height'),
    cons.SLInt32('hotspot_x'),
    cons.SLInt32('hotspot_y'),
)

slp = cons.Struct('header',
    cons.String('version', 4),
    cons.ULInt32('num_frames'),
    cons.String('comment', 24),
    cons.MetaRepeater(lambda ctx: ctx['num_frames'], frame)
)

boundary = cons.Struct('boundaries',
    cons.ULInt16('left'),
    cons.ULInt16('right'),
)

cmd_offset = cons.Struct('cmd_offsets',
    cons.ULInt32('offset')
)

from PIL import Image, ImageDraw

num = 59

def build_palette(filename):
    img = Image.open(filename)
    x_offset, y_offset = 6, 6
    tile_width, tile_height = 28, 22

    palette = {}
    for tile_y in xrange(16):
        for tile_x in xrange(16):
            x, y = tile_x * tile_width + x_offset, tile_y * tile_height + y_offset
            palette[tile_y * 16 + tile_x] = img.getpixel((x, y))

    return palette

PALETTE = build_palette('aoe1gamepalette1.png')

from pprint import pprint
pprint( PALETTE)
#i = Image.new('RGB', (16*32, 16*32))
#d = ImageDraw.ImageDraw(i)
#for x in xrange(16):
#    for y in xrange(16):
#        d.rectangle((x*32, y*32, x*32+32, y*32+32), fill=PALETTE[x*16+y])
#i.save('palette.png', 'png')

PLAYER = 1

def build_image(stream, frame):
    img = Image.new('RGBA', (frame.width, frame.height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Draw transparency mask
    lboundaries = []
    stream.seek(frame.outline_table_offset)
    for y in xrange(frame.height):
        bounds = boundary.parse_stream(stream)
        lboundaries.append(bounds.left)
        draw.line((0, y, bounds.left, y), fill=(255, 255, 255, 0))
        draw.line((frame.width, y, frame.width - bounds.right, y), fill=(255, 255, 255, 0))

    # Draw all the rest.
    stream.seek(frame.cmd_table_offset)

    # read the command table for each row
    command_offsets = []
    for y in xrange(frame.height):
        command_offsets.append(cmd_offset.parse_stream(stream).offset)

    stream.seek(command_offsets[0])

    x = lboundaries[0]
    y = 0

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
        return (opcode >> 4) + _get_byte()

    def _draw_pixels(amount, palette_index):
        assert x + amount <= frame.width
        if palette_index is None:
            color = (255, 255, 255, 0)
        else:
            color = PALETTE[palette_index] + (255,)
        if amount == 1:
            draw.point((x, y), fill=color)
        else:
            draw.line((x, y, x + amount, y), fill=color)

    def _get_palette_index(player, relindex):
        return player * 16 + relindex

    while y < frame.height:
        opcode = _get_byte()
        twobit = opcode & 0b11
        fourbit = opcode & 0b1111

        if x > frame.width:
            raise Exception('%d > %d' % (x, frame.width))

        if fourbit == 0x0f:
            # end of line
#            print '================== end of line'
            y += 1
            if y < frame.height:
                x = lboundaries[y]
                if stream.tell() != command_offsets[y]:
                    raise Exception('%d but should be %d' % (stream.tell(), command_offsets[y]))
        elif fourbit == 0x06:
            # player colors
            print 'player colors'
            amount = _get_4ornext(opcode)
            for _ in xrange(amount):
                 relindex = _get_byte()
                 _draw_pixels(1, _get_palette_index(PLAYER, relindex))
                 x += 1
            # TODO!
        elif fourbit == 0x07:
            # fill
            amount = _get_4ornext(opcode)
            palette_index = _get_byte()
            _draw_pixels(amount, palette_index)
            x += amount
        elif fourbit == 0x0a:
            print 'big player colors fill'
            amount = _get_4ornext(opcode)
            _draw_pixels(amount, _get_palette_index(PLAYER, _get_byte()))
            x += amount
        elif twobit == 0:
            amount = opcode >> 2
            print 'draw', amount
            for _ in xrange(amount):
                _draw_pixels(1, _get_byte())
                x += 1
        elif twobit == 1:
            # 2ornext
            amount = opcode >> 2
            print 'skip', amount
            if amount == 0:
                amount = _get_byte()
            _draw_pixels(amount, None)
            x += amount
        elif twobit == 2:
            amount = _get_bigbig(opcode)
            print 'big draw', amount
            for _ in xrange(amount):
                _draw_pixels(1, _get_byte())
                x += 1
        elif twobit == 3:
            amount = _get_bigbig(opcode)
            print 'big skip', amount
            _draw_pixels(amount, None)
            x += amount
        else:
            raise Exception()

    return img

with open('%d.slp' % num, 'r') as f:
    data = slp.parse_stream(f)
    for idx, frame in enumerate(data.frames):
        build_image(f, frame).save('%d-%d.png' % (num, idx), 'png')
