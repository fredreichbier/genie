"""
    A module to to read Paint Shop Pro palette files like the ones
    used in Age of Empires (ASCII files starting with "JASC-PAL").
"""

class PaletteError(Exception):
    pass

def read_palette(stream):
    """
        Read the palette data from the file-like stream. Return a
        dictionary mapping palette indices to (R, G, B) tuples.
    """
    # "JASC-PAL" header
    line = stream.readline()
    if line.strip() != 'JASC-PAL':
        raise PaletteError('Expected "JASC-PAL", got %r' % line)
    # Discard palette version
    version = stream.readline().strip()
    # Number of entries.
    line = stream.readline().strip()
    try:
        entries = int(line)
    except ValueError:
        raise PaletteError('Expected number, got %r' % line)
    # And now, colors!
    palette = {}
    for index in xrange(entries):
        palette[index] = tuple(map(int, stream.readline().strip().split(' ')))
    return palette

