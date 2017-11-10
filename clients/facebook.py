import requests

class FacebookMessenger(object):
    def __init__(self, options):
        self.access_token = options.get('PAGE_ACCESS_TOKEN', '')
        self.verify_token = options.get('VERIFY_TOKEN', '')
        self.valid_sender_ids = options.get('VALID_SENDER_IDS', [])
        self.graph_url = 'https://graph.facebook.com/v2.6'

    def is_valid_sender(self, sender_id):
        return sender_id in self.valid_sender_ids

    def subscribe(self):
        return requests.post('{0}/me/subscribed_apps'.format(self.graph_url), { 'access_token': self.access_token })

    def match_verify_token(self, passed_verify_token):
        return self.verify_token == passed_verify_token

    def send_text_message(self, recipient_id, message):
        request_endpoint = '{0}/me/messages'.format(self.graph_url)
        response = requests.post(
            request_endpoint,
            params={ 'access_token': self.access_token },
            json={ 'recipient': { 'id': recipient_id }, 'notification_type': 'REGULAR', 'message': { 'text': message }}
        )
        result = response.json()
        return result