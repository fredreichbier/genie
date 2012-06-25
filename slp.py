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

from PIL import Image, ImageDraw

num = 666

def build_image(stream, frame):
    stream.seek(frame.outline_table_offset)

    img = Image.new('RGBA', (frame.width, frame.height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)
    for y in xrange(frame.height):
        bounds = boundary.parse_stream(f)
        draw.line((0, y, bounds.left, y), fill=(255, 255, 255, 0))
        draw.line((frame.width, y, frame.width - bounds.right, y), fill=(255, 255, 255, 0))

    del draw
    return img

with open('%d.slp' % num, 'r') as f:
    data = slp.parse_stream(f)
    for frame in data.frames:
        build_image(f, frame).save('%d.png' % num, 'png')
