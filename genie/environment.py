import os.path
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from .drs import DRSFile
from .slp import SLPFile
from .palette import read_palette
from .cabinet import Cabinet, normpath

PALETTE_OFFSET = 50500
INTERFAC_DRS = 'interfac.drs'

class Environment(object):
    """
        A manager for a data directory.
    """
    def __init__(self, path):
        self.path = path
        self.cabinet = Cabinet()
        self._drs_files = {}

    def get_drs(self, basename):
        """
            Return the corresponding `DRSFile` instance.
        """
        filename = normpath(os.path.join(self.path, basename))
        stream = self.cabinet.get_file(filename)
        if filename not in self._drs_files:
            self._drs_files[filename] = DRSFile(stream)
        return self._drs_files[filename]

    def get_palette(self, idx):
        """
            Return the palette dictionary with the index *idx*.
        """
        drs = self.get_drs(INTERFAC_DRS)
        return read_palette(StringIO(drs.get_data(PALETTE_OFFSET + idx)))

    def get_slp(self, drs_filename, res_id, image_adapter_cls):
        """
            Get a `SLPFile` object. Retrieve the correct palette.

            :todo: the *correct* palette
        """
        drs = self.get_drs(drs_filename)
        return SLPFile(StringIO(drs.get_data(res_id)),
                       self.get_palette(0),
                       image_adapter_cls)
