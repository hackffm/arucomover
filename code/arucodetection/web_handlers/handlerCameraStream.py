import io
import numpy as np
import tornado.web

from multiprocessing import shared_memory
from PIL import Image, ImageDraw


class HandlerCameraStream(tornado.web.RequestHandler):
    def initialize(self, video_config):
        self.height = int(video_config["height"])
        self.shm_video = shared_memory.SharedMemory(name=video_config["shm_video_name"])
        self.width = int(video_config["width"])

    def image_from_videostream(self):
        shared_arr = np.ndarray((self.height, self.width), dtype=np.int64, buffer=self.shm_video.buf)
        img = Image.fromarray(shared_arr, 'RGB')
        return img

    @tornado.gen.coroutine
    def get(self):
        o = io.BytesIO()
        s = ''              # cleanup in asynch loop
        img = self.image_from_videostream()
        # get valid s before creating headers as we need the length
        img.save(o, format="JPEG")
        s = o.getvalue()
        self.set_header('Content-type', 'image/jpeg')
        self.set_header('Content-length', len(s))
        self.write(s)
        # get end
        return
