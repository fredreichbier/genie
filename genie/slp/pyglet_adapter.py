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

ORIGINAL_ANIMATIONS = [
    2, # south
    1, # southwest
    4, # ...
    7,
    8,
]
MIRRORED_ANIMATIONS = {
    7: 9, # 9 (northeast) is 7 (northwest) mirrored
    4: 6, # ...
    1: 3,
}
DIRECTIONS_IN_SLP = 5

class AnimationError(Exception):
    pass

def load_aoe_animations(stream, slp_file, duration=0.1):
    """
        Load AOE animations. Return a dictionary ``{ direction: Animation instance }``
        where *direction* is a number from 0-9. Look at your numpad.

        The actual count of frames per direction varies, but there always are
        5 directions stored in one SLP file, so we can calculate the frame count
        per animation from that.
    """
    anims = {}
    if len(slp_file.frames) % DIRECTIONS_IN_SLP:
        raise AnimationError('incompatible frame count: %d' % len(slp_file.frames))
    frames_per_direction = len(slp_file.frames) // DIRECTIONS_IN_SLP
    # load original (in-file) animations
    for idx, direction in enumerate(ORIGINAL_ANIMATIONS):
        anims[direction] = load_animation(stream, slp_file,
                                    (
                                        idx * frames_per_direction,
                                        (idx + 1) * frames_per_direction - 1
                                    ),
                                    duration,
                                    False)
        if direction in MIRRORED_ANIMATIONS:
            anims[MIRRORED_ANIMATIONS[direction]] = load_animation(stream, slp_file,
                                        (
                                            idx * frames_per_direction,
                                            (idx + 1) * frames_per_direction - 1
                                        ),
                                        duration,
                                        True)
    return anims
