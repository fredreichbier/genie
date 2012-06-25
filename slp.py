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

with open('%d.slp' % num, 'r') as f:
    data = slp.parse_stream(f)
    for frame in data.frames:
        f.seek(frame.outline_table_offset)
        img = Image.new('RGB', (frame.width, frame.height), (255, 255, 255))
        draw = ImageDraw.Draw(img)
        for y in xrange(frame.height):
            bounds = boundary.parse_stream(f)
#            if bo.left == 0x8000:
#                print 'HAHAH'
            draw.line((0, y, bounds.left, y), fill=128)
            draw.line((frame.width, y, frame.width - bounds.right, y), fill=128)
        del draw
        img.save('%d.png' % num, 'png')
