#!/usr/bin/env python
import os

import tornado.web
import tornado.websocket
import tornado.httpserver
from tornado import gen
from tornado.ioloop import IOLoop


from web_handlers import HandlerCamera
from web_handlers import HandlerCameraStream
from web_handlers import HandlerIndexPage
from web_handlers import HandlerShutdown
from web_handlers import HandlerWebSockets


def current_modus_updated(current_modus, helper, m_modus):
    m_modus_dict = dict(m_modus)
    try:
        new_modus = {}
        # do not remove next line as this is needed to avoid reference changes !
        helper.dict_copy(m_modus_dict, new_modus)
        if helper.is_different_modus(current_modus, new_modus):
            helper.dict_copy(new_modus, current_modus)
        else:
            pass
    except Exception as e:
        helper.log_add_text('current_modus_updated', 'Error:' + str(e))
    return current_modus


@gen.coroutine
def generate_message_to_sockets(configuration, helper, m_modus):
    current_modus = configuration.default_mode()
    while True:
        msg = current_modus_updated(current_modus, helper, m_modus)
        if len(HandlerWebSockets.connections) > 0:
            yield [con.write_message(msg) for con in HandlerWebSockets.connections]
        yield gen.sleep(1.0)


class WebApplication(tornado.web.Application):
    def __init__(self, l_lock, configuration, helper, q_message, video_config):
        current_path = os.path.dirname(os.path.abspath(__file__))
        web_resources = current_path + '/web_resources'

        handlers = [
            (r'/', HandlerIndexPage, dict(configuration=configuration, helper=helper)),
            (r'/arucodetection/(.*)', tornado.web.StaticFileHandler, {'path': web_resources}),
            (r'/camera', HandlerCamera, dict(l_lock=l_lock, configuration=configuration, q_message=q_message)),
            (r'/camera/stream.jpeg', HandlerCameraStream, dict(video_config=video_config)),
            (r'/shutdown', HandlerShutdown, dict(helper=helper, l_lock=l_lock, q_message=q_message)),
            (r'/websockets', HandlerWebSockets, dict(helper=helper, ))
        ]

        debug = configuration.config['debug']
        settings = {
            'autoreload': debug,
            'debug': debug,
            'static_path': web_resources,
            'template_path': 'web_templates'
        }
        tornado.web.Application.__init__(self, handlers, **settings)


class WebServer:
    def __init__(self, name, l_lock, configuration, helper, q_message, m_modus, video_config):
        self.configuration = configuration
        self.config = configuration.config
        self.helper = helper
        self.m_modus = m_modus

        self.name = name

        port = self.config['webserver']['server_port']
        ws_app = WebApplication(l_lock, configuration, self.helper, q_message,  video_config)
        server = tornado.httpserver.HTTPServer(ws_app)

        self.log('Start web server at port:' + str(port))
        print('webserver will listen at port ' + str(port))
        server.listen(port)
        IOLoop.current().spawn_callback(generate_message_to_sockets, self.configuration, self.helper, self.m_modus)
        IOLoop.instance().start()

    def log(self, text):
        self.helper.log_add_text(self.name, 'WebServer:' + text)
