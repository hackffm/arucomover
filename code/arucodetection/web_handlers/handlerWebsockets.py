import json
import tornado.websocket


class HandlerWebSockets(tornado.websocket.WebSocketHandler):
    connections = set()
    
    def initialize(self, helper):
        self.helper = helper
    
    def log(self, text):
        self.helper.log_add_text('handlerWebsockets', text)

    # -- default events--------------------------#
    def open(self):
        self.connections.add(self)
        message = {"detect": {"distance": "0", "position": "0,0,0"}}
        self.log('new connection was opened')
        message = json.dumps(message)
        [con.write_message(message) for con in HandlerWebSockets.connections]
        return

    # currently we don't expect messages from the webfrontend
    def on_message(self, message):
        self.log('from WebSocket: ' + str(message))

    def on_close(self):
        self.connections.remove(self)
        self.log('connection closed')
