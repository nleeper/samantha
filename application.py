import tornado.web

from libs.chat_processor import ChatProcessor

from pipeline.handler import PipelineHandler
from pipeline.manager import PipelineManager

from web.handlers.facebook import FacebookHandler

class WebApplication(tornado.web.Application):
    def __init__(self):
        self._pipeline_manager = PipelineManager()
        self._chat_processor = ChatProcessor(self._pipeline_manager)

        routes_handlers = [
            (r'/ws/pipeline', PipelineHandler),
            (r'/facebook', FacebookHandler)
        ]

        tornado.web.Application.__init__(self, routes_handlers)

    def initialize(self):
        self._chat_processor.initialize()

    @property
    def pipeline_manager(self):
        return self._pipeline_manager

    @property
    def chat_processor(self):
        return self._chat_processor
