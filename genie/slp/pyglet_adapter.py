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

def load_animation(stream, slp_file, frame_ids, duration=0.1):
    """
        Load some frames from the slp fil into an `pyglet.image.Animation` instance.
        *frame_ids* is a tuple ``(first frame, last frame)`` (inclusive).
        *duration* is the number of seconds to display the frame.

        Return a `pyglet.image.Animation` instance.
    """
    anim_frames = []
    for frame_id in xrange(frame_ids[0], frame_ids[1] + 1):
        frame = slp_file.frames[frame_id]
        img = frame.parse_stream(stream, image_adapter_cls=PygletAdapter)
        anim_frames.append(AnimationFrame(img, duration))
    return Animation(anim_frames)
