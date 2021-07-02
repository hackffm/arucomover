import tornado.web
import json


class HandlerCamera(tornado.web.RequestHandler):
    def initialize(self, l_lock, configuration, q_message):
        self.configuration = configuration
        self.l_lock = l_lock
        self.q_message = q_message

    def post(self, *args):
        new_modus = ""
        try:
            camera_mode = tornado.escape.json_decode(self.request.body)
            if type(camera_mode) == str:
                new_modus = camera_mode[12:]
            if type(camera_mode) == dict:
                new_modus = str(camera_mode['camera_mode'])
                camera_mode = "camera_mode:" + new_modus
        except:
            pass
        if new_modus in self.configuration.config['camera']['mode']:
            with self.l_lock:
                self.q_message.put(camera_mode)
            self.write(json.dumps({'status': str(camera_mode)}))
        else:
            self.write(json.dumps({'status': 'mode declined'}))
        self.finish()