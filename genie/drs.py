
import construct as cons

class DRSTableAdapter(cons.Adapter):
    def _decode(self, obj, context):
        return DRSTable(obj['resource_type'],
                        obj['offset'],
                        obj['number_of_files'])

TABLE = cons.Struct('tables',
    cons.ULInt32('resource_type'),
    cons.ULInt32('offset'),
    cons.ULInt32('number_of_files'),
)

HEADER = cons.Struct('header',
    cons.String('copyright', 40, padchar='\0'),
    cons.String('version', 4),
    cons.String('file_type', 12, padchar='\0'),
    cons.ULInt32('number_of_tables'),
    cons.ULInt32('offset'),
    cons.MetaRepeater(lambda ctx: ctx['number_of_tables'], DRSTableAdapter(TABLE)),
)

EMBEDDED_FILE = cons.Struct('embedded_file',
    cons.ULInt32('res_id'),
    cons.ULInt32('offset'),
    cons.ULInt32('size'),
)

def get_file_extension(resource_type):
    """
        get the embedded file extension from the genie resource type (a 4-byte number).
    """
    return ''.join(reversed(struct.pack('=I', resource_type)[1:]))

class DRSTable(object):
    """
        A DRS table. Holds multiple embedded files of the same type.
    """
    def __init__(self, resource_type, offset, number_of_files):
        self.resource_type = resource_type
        self.offset = offset
        self.number_of_files = number_of_files

class DRSFile(object):
    """
        A representation of a DRS container file. Can read
        data from a stream, but be careful: The stream position
        WILL NEVER BE THE SAME AGAIN!!1

        Has multiple `DRSTable` objects.
    """
    def __init__(self):
        self.header = None

    def parse_stream(self, stream):
        self.header = HEADER.parse_stream(stream)

    @property
    def tables(self):
        return self.header.tables

def parse_files(drs, table):
    drs.seek(table.offset)
    files = []

    for idx in xrange(table.number_of_files):
        files.append(embedded_file.parse_stream(drs))

    return files

def get_file(drs, embedded_file):
    drs.seek(embedded_file.offset)
    return drs.read(embedded_file.size)

#with open('graphics.drs') as f:
#    header = parse_headers(f)
#    for table in header.tables:
#        ext = get_file_extension(table.resource_type)
#        for embedded_file in parse_files(f, table):
#            with open('%d.%s' % (embedded_file.res_id, ext), 'w') as fil:
#                fil.write(get_file(f, embedded_file))
