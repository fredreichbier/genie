from genie import drs

with open('graphics.drs', 'r') as f:
    fil = drs.DRSFile()
    fil.parse_stream(f)
    print fil.tables
