from tornado.websocket import WebSocketHandler

class PipelineHandler(WebSocketHandler):
    def open(self):
        self.application.pipeline.set_connection(self)
        
        # Let the pipeline know we are open and ready
        self.application.pipeline.send_notification("connect")

    def on_message(self, message):        
        self.application.pipeline.handle_message(message)
        
    def on_close(self):
        self.application.pipeline.reset()