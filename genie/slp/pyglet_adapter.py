from pyglet.image import ImageData, AnimationFrame, Animation

from .raw_adapter import RawAdapter

class PygletAdapter(RawAdapter):
    """
        An extension to the `RawAdapter`: return an `pyglet.image.ImageData` object.
    """
    def get_image(self):
        # We need to pass a negative stride here since the image
        # will be upside-down otherwise.
        return ImageData(self.width, self.height,
                        'RGBA', str(self.array), -self.stride)

class MirroredPygletAdapter(PygletAdapter):
    """
        Exactly like the above, it's just mirrored. For simplicity, since
        Age Of Empires doesn't store all the animation directions, you have
        to mirror the existing frames to get the missing images.
    """
    def _get_byte_pos(self, x, y):
        # mirror dat. ehehehehehAHAHAHAHAH
        return y * self.stride + (self.width - x) * self.pixel_size

def load_animation(stream, slp_file, frame_ids, duration=0.1, mirrored=False):
    """
        Load some frames from the slp fil into an `pyglet.image.Animation` instance.
        *frame_ids* is a tuple ``(first frame, last frame)`` (inclusive).
        *duration* is the number of seconds to display the frame.
        If the frames should be mirrored horizontally, pass True for *mirrored*.

        Return a `pyglet.image.Animation` instance.
    """
    adapter = MirroredPygletAdapter if mirrored else PygletAdapter
    anim_frames = []
    for frame_id in xrange(frame_ids[0], frame_ids[1] + 1):
        frame = slp_file.frames[frame_id]
        img = frame.parse_stream(stream, image_adapter_cls=adapter)
        anim_frames.append(AnimationFrame(img, duration))
    return Animation(anim_frames)

ANIMATION_MAP = {
    2: (0, 9, False), # south: frames 0-9, not mirrored
    1: (10, 19, False), # southwest: frames 10-19, not mirrored
    4: (20, 29, False), # west: ...
    7: (30, 39, False), # northwest
    8: (40, 49, False), # north
    9: (30, 39, True), # northeast is northwest, but mirrored
    6: (20, 29, True), # east is west mirrored
    3: (10, 19, True), # southeast is southwest mirrored
}

def load_aoe_animations(stream, slp_file, duration=0.1):
    """
        Load AOE animations. Return a dictionary ``{ direction: Animation instance }``
        where *direction* is a number from 0-9. Look at your numpad.
    """
    anims = {}
    for direction, frame_ids in ANIMATION_MAP.iteritems():
        anims[direction] = load_animation(stream, slp_file,
                                    (frame_ids[0], frame_ids[1]),
                                    duration,
                                    frame_ids[2])
    return anims
