from tornado.websocket import WebSocketHandler

class PipelineHandler(WebSocketHandler):
    def open(self, *args):
        self.application.pipeline_manager.set_connection(self)
        
        # Let the pipeline know we are open and ready
        self.application.pipeline_manager.send_notification("connect")

    def on_message(self, message):        
        self.application.pipeline_manager.handle_message(message)
        
    def on_close(self):
        self.application.pipeline_manager.reset()