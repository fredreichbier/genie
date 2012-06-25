from genie import slp
#from genie.slp.pil_adapter import PILAdapter
from genie.slp.raw_adapter import RawAdapter

from PIL import Image

num = 663
with open('%d.slp' % num, 'r') as f:
    fil = slp.SLPFile(RawAdapter, f)
    for idx, frame in enumerate(fil.frames):
        width, height, data = frame.parse_stream(f)
        image = Image.frombuffer('RGBA', (width, height), data, 'raw', 'RGBA', 0, 1)
        image.save('%d-%d.png' % (num, idx), 'png')
