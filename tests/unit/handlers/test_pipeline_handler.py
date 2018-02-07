from mock import MagicMock

from tornado import gen
from tornado.testing import AsyncHTTPTestCase, gen_test
from tornado.web import Application
from tornado.websocket import websocket_connect

from handlers.pipeline import PipelineHandler
from libs.pipeline_manager import PipelineManager

class TestPipelineHandler(AsyncHTTPTestCase):
    pipeline_mock = None

    def get_app(self):
        app = Application([
            (r'/ws/pipeline', PipelineHandler)
        ])

        self.pipeline_mock = MagicMock(spec=PipelineManager)
        app.pipeline = self.pipeline_mock

        return app

    @gen.coroutine
    def ws_connect(self, path, compression_options=None):
        ws = yield websocket_connect(
            'ws://localhost:%d%s' % (self.get_http_port(), path),
            compression_options=compression_options)
        raise gen.Return(ws)

    @gen_test
    def test_websocket(self):
        ws = yield self.ws_connect('/ws/pipeline')

        sent_message = 'my message'
        ws.write_message(sent_message)

        self.pipeline_mock.set_connection.assert_called_once()
        self.pipeline_mock.send_notification.assert_called_once_with('registered')

        # This sucks, but haven't figured out how to wait for close to finish.
        ws.close()
        yield gen.sleep(0.1)

        self.pipeline_mock.reset.assert_called_once()