import config

from mock import Mock, MagicMock
from tornado.testing import gen_test
from tornado.concurrent import Future

from base import BaseAsyncTestCase

from clients.chat.types import ClientTypes
from libs.plugin_manager import PluginManager
from libs.chat_processor import ChatProcessor

class TestChatProcessor(BaseAsyncTestCase):

    def setUp(self):
        self.msg_parser_mock = self.mock('libs.chat_processor.MessageParser')
        self.queue_mock = self.mock('libs.chat_processor.tornado.queues.Queue')
        self.fb_mock = self.mock('libs.chat_processor.FacebookMessenger')

        self.plugin_mock = MagicMock(spec=PluginManager)

        self.chat_processor = ChatProcessor(self.plugin_mock)

    def test_constructor(self):
        self.assertEqual(self.chat_processor._plugin_manager, self.plugin_mock)
        self.assertEqual(self.chat_processor._queue, self.queue_mock.return_value)
        self.assertEqual(self.chat_processor._message_parser, self.msg_parser_mock.return_value)

        self.assertEqual(len(self.chat_processor._clients), 1)
        self.assertEqual(self.chat_processor._clients[ClientTypes.FACEBOOK], self.fb_mock.return_value)
        self.fb_mock.assert_called_once_with(config.FACEBOOK)

        self.assertEqual(len(self.chat_processor._pending_questions), 0)

    def test_initialize(self):
        fb_subscribe_mock = Mock()
        self.fb_mock.return_value.subscribe = fb_subscribe_mock

        self.chat_processor.initialize()
        fb_subscribe_mock.assert_called_once()

    def test_is_valid_sender(self):
        sender_id = 'sender'

        valid_sender_mock = Mock(return_value=True)
        self.fb_mock.return_value.is_valid_sender = valid_sender_mock

        response = self.chat_processor.is_valid_sender(ClientTypes.FACEBOOK, sender_id)

        self.assertTrue(response)
        valid_sender_mock.assert_called_once_with(sender_id)

    def test_verify_client(self):
        verify_token = 'token'

        verify_mock = Mock(return_value=True)
        self.fb_mock.return_value.match_verify_token = verify_mock

        response = self.chat_processor.verify_client(ClientTypes.FACEBOOK, verify_token)

        self.assertTrue(response)
        verify_mock.assert_called_once_with(verify_token)

    @gen_test
    def test_queue(self):
        data = {}
        put_response = {}
        queue_future = Future()

        put_mock = Mock(return_value=queue_future)
        self.queue_mock.return_value.put = put_mock
        queue_future.set_result(put_response)

        response = yield self.chat_processor.queue(data)

        put_mock.assert_called_once_with(data)
        # self.assertEqual(response, put_response)
