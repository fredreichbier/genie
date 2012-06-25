from genie import slp
from genie.slp.pil_adapter import PILAdapter

num = 216
with open('%d.slp' % num, 'r') as f:
    fil = slp.SLPFile(PILAdapter, f)
    for idx, frame in enumerate(fil.frames):
        image = frame.parse_stream(f)
        image.save('%d-%d.png' % (num, idx), 'png')
