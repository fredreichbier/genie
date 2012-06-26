import sys
from StringIO import StringIO

import pyglet

from genie import slp, drs
from genie.slp.pyglet_adapter import PygletAdapter, load_aoe_animations

try:
    num = int(sys.argv[1])
except (ValueError, IndexError):
    print 'python view_slp.py NUMBER [PLAYER] [DRS_FILE]'
    sys.exit(1)

try:
    player = int(sys.argv[2])
except IndexError:
    player = 1
except ValueError:
    print 'Wat? `%s`' % sys.argv[2]
    sys.exit(1)

try:
    drs_filename = sys.argv[3]
except IndexError:
    drs_filename = 'graphics.drs'

BAR_HEIGHT = 12

frames = []
with open(drs_filename, 'r') as stream:
    drs_file = drs.DRSFile(stream)
    slp_stream = StringIO(drs_file.get_data(num))
    slp_file = slp.SLPFile(PygletAdapter, slp_stream)
    for frame in slp_file.frames:
        frames.append(frame.parse_stream(slp_stream))

current = 0
window = pyglet.window.Window(width=100, height=100)
sprite = pyglet.sprite.Sprite(frames[0])
label = pyglet.text.Label('Foo', font_size=12, x=0, y=0)

def display(frame):
    width, height = frame.width, frame.height
    window.width = width
    window.height = height + BAR_HEIGHT
    sprite.image = frame
    sprite.set_position(frame.anchor_x, frame.anchor_y + BAR_HEIGHT)
    label.text = '#%d (%d total)' % (current, len(frames))

display(frames[0])

@window.event
def on_draw():
    window.clear()
    sprite.draw()
    label.draw()

@window.event
def on_key_press(symbol, modifiers):
    global current
    new_current = current
    if symbol == pyglet.window.key.RIGHT:
        new_current += 1
    if symbol == pyglet.window.key.LEFT:
        new_current -= 1
    if new_current != current:
        if new_current < 0:
            new_current = len(frames) - 1
        current = new_current % len(frames)
        display(frames[current])

@window.event
def on_key_release(symbol, modifiers):
    pass

pyglet.app.run()
