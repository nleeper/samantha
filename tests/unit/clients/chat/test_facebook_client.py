from mock import Mock

from base import BaseTestCase

from clients.chat.facebook import FacebookMessenger

class TestFacebookClient(BaseTestCase):

    valid_sender_id = 'id1'

    default_opts = { 'PAGE_ACCESS_TOKEN': 'access_token',
                     'VERIFY_TOKEN': 'verify_token',
                     'VALID_SENDER_IDS': [valid_sender_id, 'id2'] }

    def setUp(self):
        self.post_mock = self.mock('clients.chat.facebook.requests.post')

        self.messenger = FacebookMessenger(self.default_opts)

    def test_constructor(self):
        self.assertEqual(self.messenger._access_token, self.default_opts.get('PAGE_ACCESS_TOKEN'))
        self.assertEqual(self.messenger._verify_token, self.default_opts.get('VERIFY_TOKEN'))
        self.assertEqual(self.messenger._valid_sender_ids, self.default_opts.get('VALID_SENDER_IDS'))

    def test_constructor_uses_defaults(self):
        default_messenger = FacebookMessenger({})

        self.assertEqual(default_messenger._access_token, '')
        self.assertEqual(default_messenger._verify_token, '')
        self.assertEqual(default_messenger._valid_sender_ids, [])
        self.assertEqual(default_messenger._graph_url, 'https://graph.facebook.com/v2.6')

    def test_is_valid_sender(self):
        invalid_sender_id = 'id3'

        self.assertTrue(self.messenger.is_valid_sender(self.valid_sender_id))
        self.assertFalse(self.messenger.is_valid_sender(invalid_sender_id))

    def test_subscribe(self):
        self.messenger.subscribe()
        self.post_mock.assert_called_once_with('{0}/me/subscribed_apps'.format(self.messenger._graph_url), 
                                               params = { 'access_token': self.messenger._access_token })

    def test_match_verify_token(self):
        self.assertTrue(self.messenger.match_verify_token('verify_token'))

    def test_send_text_message(self):
        recipient_id = 'rec1'
        message = 'text'

        json_mock = Mock()
        self.post_mock.return_value.json = json_mock

        self.messenger.send_text_message(recipient_id, message)

        self.post_mock.assert_called_once_with('{0}/me/messages'.format(self.messenger._graph_url),
                                               params = { 'access_token': self.messenger._access_token },
                                               json = { 'messaging_type': 'RESPONSE',
                                                        'notification_type': 'REGULAR',
                                                        'recipient': { 'id': recipient_id },
                                                        'message': { 'text': message } })

        json_mock.assert_called_once()
        
    
    def test_send_choices_message(self):
        recipient_id = 'rec2'
        message = 'choices'
        choices = [{ 'key': 1, 'value': 'test' }, { 'key': 2, 'value': 'test2' }]

        json_mock = Mock()
        self.post_mock.return_value.json = json_mock

        self.messenger.send_choices_message(recipient_id, message, choices)

        self.post_mock.assert_called_once_with('{0}/me/messages'.format(self.messenger._graph_url),
                                        params = { 'access_token': self.messenger._access_token },
                                        json = { 'messaging_type': 'RESPONSE',
                                                 'notification_type': 'REGULAR',
                                                 'recipient': { 'id': recipient_id },
                                                 'message': { 'text': message,
                                                              'quick_replies': [
                                                                 { 'content_type': 'text', 'payload': 1, 'title': 'test' },
                                                                 { 'content_type': 'text', 'payload': 2, 'title': 'test2' }
                                                             ] } })

        json_mock.assert_called_once()