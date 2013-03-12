"""
    Read palettes from a `Interfac.drs` file.
"""

import sys
from pprint import pprint
from cStringIO import StringIO

from genie.drs import DRSFile
from genie.palette import read_palette

try:
    filename = sys.argv[1]
    try:
        palette_index = int(sys.argv[2])
    except IndexError:
        palette_index = 1
except (IndexError, ValueError):
    print 'Usage: python read_palette.py interfac.drs [palette index]'
    sys.exit(1)

RES_ID_OFFSET = 50500

with open(filename, 'r') as f:
    drs_file = DRSFile(f)
    res_id = RES_ID_OFFSET + palette_index
    pal_stream = StringIO(drs_file.get_data(res_id))
    palette = read_palette(pal_stream)
    pprint(palette)
