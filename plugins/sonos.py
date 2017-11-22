import json

import tornado.gen

class Sonos(object):
    def __init__(self, manager):
        self._manager = manager 
        self._intent_map = { 'play_artist': 'sonos.play_artist', 'speaker_list': 'sonos.speakers' }

    def supported_intents(self):
        return list(self._intent_map.keys())
    
    @tornado.gen.coroutine
    def handle(self, intent, entities):
        method = self._to_method(intent)
        params = self._to_params(entities)

        response = yield self._manager.pipeline.send_request_response(method, params)
        raise tornado.gen.Return(self._process_response(method, response))

    def _process_response(self, method, response):
        if response['error'] is None:
            result = response['result']
            if result['success'] is True:
                if method == 'sonos.speakers':
                    speakers = ', '.join([v['name'] for k, v in result['speakers'].iteritems()])
                    return 'I found these speakers: %s' % speakers
                elif method == 'sonos.play_artist':
                    return 'Your artist is playing. Enjoy!'
                else:
                    return "I'm not sure what you wanted me to do"
            else:
                return 'Sorry, an unknown error occurred'
        else:
            return response['error']

    def _to_method(self, intent):
        return self._intent_map[intent]

    def _to_params(self, entities):
        return {e['entity']: e['value'] for e in entities}