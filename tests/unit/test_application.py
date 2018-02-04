from base import BaseTestCase

from handlers.facebook import FacebookHandler
from handlers.pipeline import PipelineHandler

from application import WebApplication

class TestApplication(BaseTestCase):

    def setUp(self):
        self.pipeline_mock = self.mock('application.PipelineManager')
        self.plugin_mock = self.mock('application.PluginManager')
        self.chat_mock = self.mock('application.ChatProcessor')
        self.tornado_mock = self.mock('application.Application.__init__')

        self.app = WebApplication()

    def testConstructor(self):
        self.assertEqual(self.app.pipeline, self.pipeline_mock.return_value)
        self.assertEqual(self.app.chat_processor, self.chat_mock.return_value)
        self.assertEqual(self.app.plugins, self.plugin_mock.return_value)

        self.pipeline_mock.assert_called_once()
        self.plugin_mock.assert_called_once_with(self.app.pipeline)
        self.chat_mock.assert_called_once_with(self.app.plugins)

        self.tornado_mock.assert_called_once_with(self.app, [(r'/ws/pipeline', PipelineHandler), (r'/facebook', FacebookHandler)])

    def testInitialize(self):
        self.app.initialize()
        self.chat_mock.assert_called_once()