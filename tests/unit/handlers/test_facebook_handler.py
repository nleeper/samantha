import json

from mock import MagicMock

from tornado.concurrent import Future
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application

from clients.chat.types import ClientTypes
from handlers.facebook import FacebookHandler
from libs.chat_processor import ChatProcessor

class TestFacebookhandler(AsyncHTTPTestCase):
    chat_mock = None

    def get_app(self):
        app = Application([
            (r'/facebook', FacebookHandler)
        ])

        self.chat_mock = MagicMock(spec=ChatProcessor)
        app.chat_processor = self.chat_mock

        return app

    def test_get_verify_client(self):
        hub_token = 'token'
        hub_challenge = 'challenge'

        self.chat_mock.verify_client.return_value = True

        response = self.fetch(
            '/facebook?hub.verify_token=%s&hub.challenge=%s' % (hub_token, hub_challenge),
            method='GET',
            follow_redirects=False)

        self.chat_mock.verify_client.assert_called_once_with(ClientTypes.FACEBOOK, hub_token)

        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, hub_challenge)

    def test_get_invalid_token(self):
        hub_token = 'token'
        hub_challenge = 'challenge'

        self.chat_mock.verify_client.return_value = False

        response = self.fetch(
            '/facebook?hub.verify_token=%s&hub.challenge=%s' % (hub_token, hub_challenge),
            method='GET',
            follow_redirects=False)

        self.chat_mock.verify_client.assert_called_once_with(ClientTypes.FACEBOOK, hub_token)

        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, 'Invalid verification token')

    def test_post_queue_message(self):
        sender_id = 'sender'
        message = 'post message'
        queue_future = Future()

        self.chat_mock.is_valid_sender.return_value = True
        self.chat_mock.queue.return_value = queue_future
        queue_future.set_result(True)

        message_obj = { 
            'entry': [ 
                { 
                    'messaging': [ 
                        { 
                            'sender': { 
                                'id': sender_id 
                            }, 
                            'message': { 
                                'text': message 
                            } 
                        } 
                    ] 
                } 
            ] 
        }

        response = self.fetch(
            '/facebook',
            method='POST',
            body=json.dumps(message_obj),
            follow_redirects=False)

        self.chat_mock.queue.assert_called_once_with([dict(client_type=ClientTypes.FACEBOOK, recipient_id=sender_id, message=message)])
        self.chat_mock.is_valid_sender.assert_called_once_with(ClientTypes.FACEBOOK, sender_id)

        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, 'Success')

    def test_post_no_queue_if_invalid_sender(self):
        sender_id = 'sender'
        message = 'post message'
        queue_future = Future()

        self.chat_mock.is_valid_sender.return_value = False
        self.chat_mock.queue.return_value = queue_future
        queue_future.set_result(True)

        message_obj = { 
            'entry': [ 
                { 
                    'messaging': [ 
                        { 
                            'sender': { 
                                'id': sender_id 
                            }, 
                            'message': { 
                                'text': message 
                            } 
                        } 
                    ] 
                } 
            ] 
        }

        response = self.fetch(
            '/facebook',
            method='POST',
            body=json.dumps(message_obj),
            follow_redirects=False)

        self.chat_mock.queue.assert_called_once_with([])
        self.chat_mock.is_valid_sender.assert_called_once_with(ClientTypes.FACEBOOK, sender_id)

        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, 'Success')
        
    def test_post_no_queue_if_no_message(self):
        sender_id = 'sender'
        message = 'post message'
        queue_future = Future()

        self.chat_mock.is_valid_sender.return_value = False
        self.chat_mock.queue.return_value = queue_future
        queue_future.set_result(True)

        message_obj = { 
            'entry': [ 
                { 
                    'messaging': [ 
                        { 
                            'sender': { 
                                'id': sender_id 
                            }
                        } 
                    ] 
                } 
            ] 
        }

        response = self.fetch(
            '/facebook',
            method='POST',
            body=json.dumps(message_obj),
            follow_redirects=False)

        self.chat_mock.queue.assert_called_once_with([])
        self.chat_mock.is_valid_sender.assert_not_called()

        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, 'Success')

    def test_post_queue_quick_reply(self):
        sender_id = 'sender'
        message = 'post message'
        queue_future = Future()

        self.chat_mock.is_valid_sender.return_value = True
        self.chat_mock.queue.return_value = queue_future
        queue_future.set_result(True)

        message_obj = { 
            'entry': [ 
                { 
                    'messaging': [ 
                        { 
                            'sender': { 
                                'id': sender_id 
                            }, 
                            'message': {
                                'quick_reply': {
                                    'payload': message
                                }
                            }
                        } 
                    ] 
                } 
            ] 
        }

        response = self.fetch(
            '/facebook',
            method='POST',
            body=json.dumps(message_obj),
            follow_redirects=False)

        self.chat_mock.queue.assert_called_once_with([dict(client_type=ClientTypes.FACEBOOK, recipient_id=sender_id, message=message)])
        self.chat_mock.is_valid_sender.assert_called_once_with(ClientTypes.FACEBOOK, sender_id)

        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, 'Success')
