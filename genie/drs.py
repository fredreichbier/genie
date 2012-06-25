# coding: utf-8
"""
    A parser for the genie (Age of Empires, ...) DRS container file format.

    Based on the excellent documentation at http://artho.com/age/files/drs.html -
    thank you!
"""

import struct

import construct as cons

class TableAdapter(cons.Adapter):
    def _decode(self, obj, context):
        return Table(obj['resource_type'],
                        obj['offset'],
                        obj['number_of_files'],
                        dict((f.resource_id, f) for f in obj['embedded_files']))

EMBEDDED_FILE = cons.Struct('embedded_files',
    cons.ULInt32('resource_id'),
    cons.ULInt32('offset'),
    cons.ULInt32('size'),
    cons.OnDemand(
        cons.Pointer(lambda ctx: ctx['offset'],
            cons.MetaField('data', lambda ctx: ctx['size'])
        )
    )
)

TABLE = cons.Struct('tables',
    cons.ULInt32('resource_type'),
    cons.ULInt32('offset'),
    cons.ULInt32('number_of_files'),
    cons.Pointer(lambda ctx: ctx['offset'],
        cons.MetaRepeater(lambda ctx: ctx['number_of_files'],
            EMBEDDED_FILE
        )
    )
)

HEADER = cons.Struct('header',
    cons.String('copyright', 40, padchar='\0'),
    cons.String('version', 4),
    cons.String('file_type', 12, padchar='\0'),
    cons.ULInt32('number_of_tables'),
    cons.ULInt32('offset'),
    cons.MetaRepeater(lambda ctx: ctx['number_of_tables'], TableAdapter(TABLE)),
)

def get_file_extension(resource_type):
    """
        get the embedded file extension from the genie resource type (a 4-byte number).
    """
    return ''.join(reversed(struct.pack('=I', resource_type)[1:]))

class Table(object):
    """
        A DRS table. Holds multiple embedded files of the same type.

        Caution: The actual file data is read *lazily*. That means, they are
        construct `OnDemand` instances. You probably don't want *all*
        resource files to be read at once since they're just chilling in your
        memory then. If you want to access the actual data, use `get_data`;
        but of course you need to do it before closing the stream.

        If you really want to read all the embedded files into memory, use
        the `read_all` method.
    """
    def __init__(self, resource_type, offset, number_of_files, embedded_files):
        self.resource_type = resource_type
        self.offset = offset
        self.number_of_files = number_of_files
        self.embedded_files = embedded_files

    @property
    def file_extension(self):
        return get_file_extension(self.resource_type)

    def get_data(self, resource_id):
        """ get the binary data of a specific file. """
        return self.embedded_files[resource_id].data.value

    def read_all(self):
        """ read ALL THE THINGS """
        for f in self.embedded_files.itervalues():
            if not f.data.has_value:
                f.data.value

class DRSFile(object):
    """
        A representation of a DRS container file. Can read
        data from a stream, but be careful: The stream position
        WILL NEVER BE THE SAME AGAIN!!1

        Has multiple `Table` objects.
    """
    def __init__(self, stream=None):
        self.header = None
        if stream is not None:
            self.parse_stream(stream)

    def parse_stream(self, stream):
        self.header = HEADER.parse_stream(stream)

    @property
    def tables(self):
        return self.header.tables

    def get_data(self, resource_id):
        """
            get the binary data of a specific file. Raise KeyError
            if it couldn't be found.
        """
        for table in self.tables:
            try:
                return table.get_data(resource_id)
            except KeyError:
                pass
        raise KeyError(resource_id)

def get_all_files(stream):
    """
        get all embedded files from a DRS file. This yields
        (resource type, resource id, data) tuples.
    """
    drs = DRSFile(stream)
    for table in drs.tables:
        ext = table.file_extension
        for embedded in table.embedded_files.itervalues():
            yield (table.resource_type, embedded.resource_id, embedded.data.value)

