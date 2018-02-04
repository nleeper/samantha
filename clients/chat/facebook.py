import requests

class FacebookMessenger(object):
    def __init__(self, options):
        self._access_token = options.get('PAGE_ACCESS_TOKEN', '')
        self._verify_token = options.get('VERIFY_TOKEN', '')
        self._valid_sender_ids = options.get('VALID_SENDER_IDS', [])
        self._graph_url = 'https://graph.facebook.com/v2.6'

    def is_valid_sender(self, sender_id):
        return sender_id in self._valid_sender_ids

    def subscribe(self):
        return requests.post('{0}/me/subscribed_apps'.format(self._graph_url), params = { 'access_token': self._access_token })

    def match_verify_token(self, passed_verify_token):
        return self._verify_token == passed_verify_token

    def send_text_message(self, recipient_id, message):
        return self._send_message(recipient_id, { 'text': message })

    def send_choices_message(self, recipient_id, message, choices):
        quick_replies = [{ 'content_type': 'text', 'title': c['value'], 'payload': c['key'] } for c in choices]
        return self._send_message(recipient_id, { 'text': message, 'quick_replies': quick_replies })

    def _send_message(self, recipient_id, message, notification_type = 'REGULAR'):
        request_endpoint = '{0}/me/messages'.format(self._graph_url)
        
        response = requests.post(
            request_endpoint,
            params = { 'access_token': self._access_token },
            json = {
                'messaging_type': 'RESPONSE',
                'notification_type': notification_type,
                'recipient': { 'id': recipient_id },
                'message': message
            }
        )
        
        return response.json()