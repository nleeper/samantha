import tornado.gen
import tornado.queues

import config

from libs.message_parser import MessageParser

from clients.types import ClientTypes
from clients.facebook import FacebookMessenger

class ChatProcessor(object):
    def __init__(self, plugin_manager):
        self._plugin_manager = plugin_manager

        self._message_parser = MessageParser()
        self._queue = tornado.queues.Queue()

        self._clients = dict()
        self._clients[ClientTypes.FACEBOOK] = FacebookMessenger(config.FACEBOOK)

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
                parsed_message = self._message_parser.parse(entry['message'])

                response = yield self._plugin_manager.handle(parsed_message['intent'], parsed_message['entities'])
                self._send_response(entry, response)

    def _send_response(self, entry, response):
        self._clients[entry['client_type']].send_text_message(entry['recipient_id'], response)