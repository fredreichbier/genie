from StringIO import StringIO

import pyglet

from genie import slp, drs
from genie.slp.pyglet_adapter import PygletAdapter, load_aoe_animations

window = pyglet.window.Window()

def get_pyglet_animation(num):
    with open('graphics.drs', 'r') as stream:
        drs_file = drs.DRSFile(stream)
        slp_stream = StringIO(drs_file.get_data(num))
        slp_file = slp.SLPFile(PygletAdapter, slp_stream)
        return load_aoe_animations(slp_stream, slp_file)

anims = get_pyglet_animation(669)

sprite = pyglet.sprite.Sprite(anims[8])
sprite.set_position(300, 300)

@window.event
def on_draw():
    window.clear()
    sprite.draw()

KEYS = {
    pyglet.window.key.A: 4,
    pyglet.window.key.Q: 7,
    pyglet.window.key.W: 8,
    pyglet.window.key.E: 9,
    pyglet.window.key.D: 6,
    pyglet.window.key.C: 3,
    pyglet.window.key.X: 2,
    pyglet.window.key.Y: 1,
}

@window.event
def on_key_press(symbol, modifiers):
    if symbol in KEYS:
        sprite.image = anims[KEYS[symbol]]

@window.event
def on_key_release(symbol, modifiers):
    pass

pyglet.app.run()
