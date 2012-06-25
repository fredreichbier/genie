from genie import drs, slp

with open('graphics.drs', 'r') as f:
    for resource_type, resource_id, data in drs.get_all_files(f):
        filename = '%d.%s' % (resource_id, drs.get_file_extension(resource_type))
        with open(filename, 'w') as g:
            g.write(data)
