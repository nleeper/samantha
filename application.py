import tornado.web

from libs.chat_processor import ChatProcessor
from libs.pipeline_manager import PipelineManager
from libs.plugin_manager import PluginManager

from handlers.facebook import FacebookHandler
from handlers.pipeline import PipelineHandler

class WebApplication(tornado.web.Application):
    def __init__(self):
        self._pipeline_manager = PipelineManager()
        self._plugin_manager = PluginManager(self._pipeline_manager)
        self._chat_processor = ChatProcessor(self._plugin_manager)

        routes_handlers = [
            (r'/ws/pipeline', PipelineHandler),
            (r'/facebook', FacebookHandler)
        ]

        tornado.web.Application.__init__(self, routes_handlers)

    def initialize(self):
        self.chat.initialize()

    @property
    def pipeline(self):
        return self._pipeline_manager

    @property
    def plugins(self):
        return self._plugin_manager

    @property
    def chat(self):
        return self._chat_processor
