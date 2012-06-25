import struct

import construct as cons

def get_file_extension(resource_type):
    return ''.join(reversed(struct.pack('=I', resource_type)[1:]))

def parse_headers(drs):
    table = cons.Struct('tables',
        cons.ULInt32('resource_type'),
        cons.ULInt32('offset'),
        cons.ULInt32('number_of_files'),
#    cons.MetaRepeater(lambda ctx: ctx['number_of_files'], embedded_file),
    )

    header = cons.Struct('header',
        cons.String('copyright', 40, padchar='\0'),
        cons.String('version', 4),
        cons.String('file_type', 12, padchar='\0'),
        cons.ULInt32('number_of_tables'),
        cons.ULInt32('offset'),
        cons.MetaRepeater(lambda ctx: ctx['number_of_tables'], table),
    )

    return header.parse_stream(drs)

def parse_files(drs, table):
    drs.seek(table.offset)

    embedded_file = cons.Struct('embedded_file',
        cons.ULInt32('res_id'),
        cons.ULInt32('offset'),
        cons.ULInt32('size'),
    )

    files = []

    for idx in xrange(table.number_of_files):
        files.append(embedded_file.parse_stream(drs))

    return files

def get_file(drs, embedded_file):
    drs.seek(embedded_file.offset)
    return drs.read(embedded_file.size)

with open('graphics.drs') as f:
    header = parse_headers(f)
    for table in header.tables:
        ext = get_file_extension(table.resource_type)
        for embedded_file in parse_files(f, table):
            with open('%d.%s' % (embedded_file.res_id, ext), 'w') as fil:
                fil.write(get_file(f, embedded_file))
