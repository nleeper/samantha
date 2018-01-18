import json 

from clients.chat.types import ClientTypes

import tornado.gen
from tornado.web import RequestHandler

client_type = ClientTypes.FACEBOOK

class FacebookHandler(RequestHandler):
    def get(self):
        verify_token = self.get_argument('hub.verify_token', '')
        if (self.application.chat_processor.verify_client(client_type, verify_token)):
            self.write(self.get_argument('hub.challenge', ''))
        else:
            self.write('Invalid verification token')
    
    @tornado.gen.coroutine
    def post(self):
        entries = []

        output = json.loads(self.request.body)

        for event in output['entry']:
            messaging = event['messaging']
            for x in messaging:
                if 'message' in x:
                    message = x['message']
                    sender_id = x['sender']['id']
                    if self.application.chat_processor.is_valid_sender(client_type, sender_id):
                        text = None

                        if 'quick_reply' in message:
                            text = message['quick_reply']['payload']
                        elif 'text' in message:
                            text = message['text']

                        if text:
                            entries.append(dict(client_type=client_type, recipient_id=sender_id, message=text))
                    else:
                        print 'Invalid sender id %s, skipping message' % sender_id
                else:
                    pass

        yield self.application.chat_processor.queue(entries)

        self.write("Success")
