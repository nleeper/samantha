import json

import tornado.gen

from base import BasePlugin

class Sonos(BasePlugin):
    def __init__(self, manager):
        BasePlugin.__init__(self, manager)

        self._intent_map = { 'play_genre': 'sonos.play_genre', 'play_artist': 'sonos.play_artist', 'speaker_list': 'sonos.speakers' }
    
    @tornado.gen.coroutine
    def handle(self, intent, entities):
        method = self._to_method(intent)
        params = self._to_params(entities)

        if method == 'sonos.play_artist':
            response = self._play_artist(params)
        elif method == 'sonos.play_genre':
            response = self._play_genre(params)
        elif method == 'sonos.speakers':
            response = self._get_speakers()

        return response

    def _play_genre(self, params):
        raise tornado.gen.Return({ 'message': 'Playing some genre', 'type': 'response' })

    def _play_artist(self, params):
        if not 'artist' in params:
            raise tornado.gen.Return(self._build_response('I don\'t know what artist you want me to play. Try again?', True))
        
        if not 'speaker' in params:
            raise tornado.gen.Return(self._build_question('What speaker do you want me to play music on?', 'speaker'))

        response = yield self._request('sonos.play_artist', params)

        result = response['result']
        if result['success'] is True:
            answer = 'Your artist is playing. Enjoy!'
        else:
            answer = 'I couldn\'t play the artist you wanted. Sorry!'

        raise tornado.gen.Return(self._build_response(answer))

    def _get_speakers(self):
        response = yield self._request('sonos.speakers', {})

        result = response['result']
        if result['success'] is True:
            speakers = ', '.join([v['name'] for k, v in result['speakers'].iteritems()])
            raise tornado.gen.Return(self._build_response('I found these speakers: %s' % speakers))
        else:
            raise tornado.gen.Return(self._build_response('Sorry, I couldn\'t find any speakers!', True))
