from StringIO import StringIO

import pyglet

from genie import slp, drs
from genie.slp.pyglet_adapter import PygletAdapter, load_animation

window = pyglet.window.Window()

def get_pyglet_animation(num):
    with open('graphics.drs', 'r') as stream:
        drs_file = drs.DRSFile(stream)
        slp_stream = StringIO(drs_file.get_data(num))
        slp_file = slp.SLPFile(PygletAdapter, slp_stream)
        return load_animation(slp_stream, slp_file, (0, 9))

sprite = pyglet.sprite.Sprite(get_pyglet_animation(663))

@window.event
def on_draw():
    window.clear()
    sprite.draw()

pyglet.app.run()
