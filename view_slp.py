import sys
import argparse
from StringIO import StringIO

import pyglet

from genie import slp, drs
from genie.environment import Environment
from genie.slp.pyglet_adapter import PygletAdapter, load_aoe_animations

parser = argparse.ArgumentParser(description='View SLP files.')
parser.add_argument('path', metavar='PATH', type=str,
                    help='The game data location')
parser.add_argument('res_id', metavar='RESOURCE', type=int,
                    help='The SLP resource ID')
parser.add_argument('--drs', dest='drs_filename', metavar='FILENAME', type=str,
                    default='graphics.drs',
                    help='The DRS file to open (defaults to graphics.drs)')
parser.add_argument('--player', dest='player', metavar='PLAYER', type=int,
                    default=1,
                    help='The player ID to display (defaults to 1)')

args = parser.parse_args()

env = Environment(args.path)
BAR_HEIGHT = 12

frames = []
slp_file = env.get_slp(args.drs_filename, args.res_id, PygletAdapter)
for frame in slp_file.frames:
    frames.append(frame.parse_stream())

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
