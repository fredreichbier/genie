import sys
import argparse
import traceback
import cmd
import os
import fnmatch
import subprocess
from StringIO import StringIO

import pyglet

from genie import slp, drs
from genie.environment import Environment
from genie.slp.pyglet_adapter import PygletAdapter, load_aoe_animations

BAR_HEIGHT = 12

def _get_resource_id(filename):
    return int(filename.split('.')[0])

class SLPLoader(object):
    def __init__(self, path, audio_player):
        self.env = Environment(path)
        self._drs_filename = None
        self.audio_player = audio_player
        self.palette = 0

    def _set_drs_filename(self, drs_filename):
        self._drs_filename = drs_filename

    def _get_drs_filename(self):
        return self._drs_filename

    drs_filename = property(_get_drs_filename, _set_drs_filename)

    @property
    def drs_file(self):
        return self.env.get_drs(self.drs_filename)

    def get_files(self):
        """
            yield all SLP files as tuples (resource id, pseudo-filename)
        """
        for table in self.drs_file.tables:
            for embedded in table.embedded_files.itervalues():
                fname = '%d.%s' % (embedded.resource_id, table.file_extension)
                yield (embedded.resource_id, fname)

    def show_filename(self, filename):
        """
            show the given filename. shortcut.
        """
        resource_id = _get_resource_id(filename)
        self.show_resource(resource_id)

    def play_filename(self, filename):
        self.play_resource(_get_resource_id(filename))

    def play_resource(self, resource_id):
        """
            Play a WAV file!
        """
        player = subprocess.Popen(self.audio_player, stdin=subprocess.PIPE, shell=True)
        wav_data = self.drs_file.get_data(resource_id)
        player.communicate(wav_data)

    def get_frames(self, resource_id):
        slp_file = self.env.get_slp(self.drs_filename, resource_id, PygletAdapter, self.palette)
        return [frame.parse_stream() for frame in slp_file.frames]

    def show_resource(self, resource_id):
        frames = self.get_frames(resource_id)
        display_slp(frames)

    def get_matching(self, pattern):
        """
            yield (resource id, pseudo-filename) patterns for all SLP files
            matching the glob-style *pattern*.
        """
        for resource_id, filename in self.get_files():
            # TODO: could be more efficient.
            if fnmatch.fnmatch(filename, pattern):
                yield (resource_id, filename)

class SLPView(object):
    """
        A simple display window for SLP files.

        Exits the pyglet main loop when the user presses q.
    """
    def __init__(self, frames):
        self.current = 0
        self.frames = frames

        self.window = pyglet.window.Window(width=100, height=100)
        self.window.push_handlers(self)
        self.sprite = pyglet.sprite.Sprite(self.frames[0])
        self.label = pyglet.text.Label('Foo', font_size=12, x=0, y=0)

        self.display(frames[0])

    def display(self, frame):
        self.sprite.image = frame
        self.label.text = '#%d (%d total)' % (self.current, len(self.frames))
        self.resize_window()

    def resize_window(self):
        self.sprite.set_position(
                self.frames[self.current].anchor_x * self.sprite.scale,
                self.frames[self.current].anchor_y * self.sprite.scale + BAR_HEIGHT)
        self.window.width = max(self.label.content_width, self.sprite.width)
        self.window.height = self.sprite.height + BAR_HEIGHT

    def on_draw(self):
        self.window.clear()
        self.sprite.draw()
        self.label.draw()

    def zoom(self, factor):
        self.sprite.scale += factor * 0.2
        self.resize_window()

    def on_key_press(self, symbol, modifiers):
        new_current = self.current
        if symbol == pyglet.window.key.RIGHT:
            new_current += 1
        if symbol == pyglet.window.key.LEFT:
            new_current -= 1
        if symbol == pyglet.window.key.Q:
            self.window.close()
            pyglet.app.exit()
        if symbol == pyglet.window.key.PLUS:
            self.zoom(1)
        if symbol == pyglet.window.key.MINUS:
            self.zoom(-1)
        if new_current != self.current:
            if new_current < 0:
                new_current = len(self.frames) - 1
            self.current = new_current % len(self.frames)
            self.display(self.frames[self.current])

class SLPBrowser(cmd.Cmd):
    def __init__(self, loader):
        cmd.Cmd.__init__(self)
        self.prompt = 'genie> '
        self.intro = 'Welcome to browse_slp.py. You can do anything at browse_slp.py.\n'\
                     '\tYou might want to start with `drs` to see which DRS file you are\n'\
                     '\tcurrently browsing. Then, you can type `ls` to see all available\n'\
                     '\tfiles, and `play ID` to play .WAV files or `show ID` to view SLP files.'
        self.loader = loader

    def do_drs(self, filename):
        """
            Load a specified DRS file.
        """
        if filename.strip():
            self.loader.drs_filename = filename
            print "We're now browsing `%s`" % filename
        else:
            if self.loader.drs_filename is None:
                print 'No DRS file set yet.'
            else:
                print "We're current browsing %s" % self.loader.drs_filename

    def do_ls(self, pattern):
        """
            List all resources matching the given glob pattern.
        """
        if not pattern.strip():
            pattern = '*'
        names = [fname for resource_id, fname in self.loader.get_matching(pattern)]
        self.columnize(names)

    def do_show(self, name):
        """
            Show the given SLP file!
        """
        try:
            print "Now showing %r. Keys:" % name
            print "\tq\treturn to prompt"
            print "\t+/-\tzoom"
            self.loader.show_filename(name)
        except:
            traceback.print_exc()

    def do_palette(self, idx_str):
        """
            Set the palette index to use. Default is 0.
        """
        try:
            idx = int(idx_str)
        except ValueError:
            print 'Gimme an integer :-('
        self.loader.palette = idx

    def do_play(self, name):
        """
            Play the given WAV file!
        """
        try:
            print 'Now playing %r ...' % name
            self.loader.play_filename(name)
        except:
            traceback.print_exc()

def display_slp(frames):
    """ display SLP frames. blocks until the user presses q """
    view = SLPView(frames)
    pyglet.app.run()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='View SLP files.')
    parser.add_argument('path', metavar='PATH', type=str,
                        help='The game data location containing the DRS files')
    parser.add_argument('--drs', dest='drs_filename', metavar='FILENAME', type=str,
                        default='graphics.drs',
                        help='The DRS file to open (defaults to graphics.drs)')
    parser.add_argument('--audio-player', dest='player_command', metavar='COMMAND', type=str,
                        default='aplay -',
                        help='Audio player that takes WAV data from stdin. Defaults to `aplay -`.')
    parser.add_argument('--player', dest='player', metavar='PLAYER', type=int,
                        default=1,
                        help='The player ID to display (defaults to 1)')
    parser.add_argument('-c', metavar='COMMAND', type=str, dest='commands',
                        action='append',
                        help='Command to execute, can be passed multiple times.')
    parser.add_argument('--batch', dest='batch_mode', default=False,
                        action='store_true',
                        help='If this is set, the command loop is not entered.')

    args = parser.parse_args()
    loader = SLPLoader(args.path, args.player_command)
    # autoload drs
    if args.drs_filename:
        loader.drs_filename = args.drs_filename
    browser = SLPBrowser(loader)
    # execute commands
    if args.commands:
        for command in args.commands:
            browser.onecmd(command)
    if not args.batch_mode:
        browser.cmdloop()
