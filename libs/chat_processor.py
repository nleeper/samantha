import hashlib

import tornado.gen
import tornado.queues

import config

from libs.message_parser import MessageParser

from clients.chat.types import ClientTypes
from clients.chat.facebook import FacebookMessenger

class ChatProcessor(object):
    def __init__(self, plugin_manager):
        self._plugin_manager = plugin_manager

        self._message_parser = MessageParser()
        self._queue = tornado.queues.Queue()

        self._clients = dict()
        self._clients[ClientTypes.FACEBOOK] = FacebookMessenger(config.FACEBOOK)

        self._pending_questions = {}

    def initialize(self):
        for k in self._clients:
            self._clients[k].subscribe()

    def is_valid_sender(self, client_type, sender_id):
        return self._clients[client_type].is_valid_sender(sender_id)

    def verify_client(self, client_type, verify_token):
        return self._clients[client_type].match_verify_token(verify_token)

    @tornado.gen.coroutine
    def queue(self, data):
        yield self._queue.put(data)

    @tornado.gen.coroutine
    def process(self):
        while True:
            entries = yield self._queue.get()
            for entry in entries:
                conversation_id = self._build_conversation_id(entry)

                if conversation_id in self._pending_questions:
                    question = self._pending_questions[conversation_id]
                    del self._pending_questions[conversation_id]

                    intent = question['intent']
                    entities = question['entities']

                    entities.append({ 'entity': question['question_entity'], 'value': entry['message'] })
                else:
                    parsed_message = self._message_parser.parse(entry['message'])

                    intent = parsed_message['intent']
                    entities = parsed_message['entities']

                response = yield self._plugin_manager.handle(intent, entities)
                if response['type'] == 'question':
                    self._pending_questions[conversation_id] = { 'intent': intent, 'entities': entities, 'question_entity': response['question_entity'] }
                    
                    if 'choices' in response:
                        self._send_choices_response(entry, response['message'], response['choices'])
                        continue
                
                self._send_response(entry, response['message'])

    def _send_response(self, entry, response):
        self._clients[entry['client_type']].send_text_message(entry['recipient_id'], response)

    def _send_choices_response(self, entry, response, choices):
        self._clients[entry['client_type']].send_choices_message(entry['recipient_id'], response, choices)

    def _build_conversation_id(self, entry):
        return hashlib.sha256('%s-%s' % (entry['client_type'], entry['recipient_id'])).hexdigest()