import json
import spotipy
import config
import random

from tornado.gen import coroutine, Return
from spotipy.oauth2 import SpotifyClientCredentials

from base import BasePlugin

class Sonos(BasePlugin):
    def __init__(self, manager):
        BasePlugin.__init__(self, manager)

        self._spotify = spotipy.Spotify(client_credentials_manager=
                                        SpotifyClientCredentials(client_id=config.SPOTIFY.get('CLIENT_ID'), 
                                                                 client_secret=config.SPOTIFY.get('CLIENT_SECRET')))
        self._intent_map = { 'play_genre': 'sonos.play_genre', 'play_artist': 'sonos.play_artist', 'speaker_list': 'sonos.speakers' }
    
    @coroutine
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
        if not 'genre' in params:
            raise Return(self._build_response('I don\'t know what genre you want me to play. Ask again?', True))

        if not 'speaker' in params:
            speakers = yield self._speaker_list()
            choices = [{ 'key': s['name'], 'value': s['name'] } for s in speakers]
            raise Return(self._build_question('What speaker do you want me to play music on?', 'speaker', choices=choices))

        genre = params['genre']
        del params['genre']

        found = self._spotify.search(genre, limit=50, type='playlist', market='US')
        if found['playlists']['total'] > 0:
            count = len(found['playlists']['items'])
            item_no = random.randint(0, count - 1)

            match = found['playlists']['items'][item_no]
            params['uri'] = match['uri']

            response = yield self._request('sonos.play_spotify', params)

            result = response['result']
            if result['success'] is True:
                answer = 'The playlist \'%s\' is now playing. Hope you like it!' % match['name']
            else:
                answer = 'I couldn\'t play the genre you wanted. Sorry!'
        else:
            answer = 'I couldn\'t find any playlists for genre %s. Try again?' % genre

        raise Return(self._build_response(answer))


    def _play_artist(self, params):
        if not 'artist' in params:
            raise Return(self._build_response('I don\'t know what artist you want me to play. Try again?', True))
        
        if not 'speaker' in params:
            speakers = yield self._speaker_list()
            choices = [{ 'key': s['name'], 'value': s['name'] } for s in speakers]
            raise Return(self._build_question('What speaker do you want me to play music on?', 'speaker', choices=choices))

        artist = params['artist']
        del params['artist']

        found = self._spotify.search(artist, limit=10, type='artist', market='US')
        if found['artists']['total'] > 0:
            match = found['artists']['items'][0]
            params['uri'] = 'spotify:artistTopTracks:%s' % match['id']

            response = yield self._request('sonos.play_spotify', params)
            
            result = response['result']
            if result['success'] is True:
                answer = 'Your artist is playing. Enjoy!'
            else:
                answer = 'I couldn\'t play the artist you wanted. Sorry!'
        else:
            answer = 'I couldn\'t find the artist %s. Try again?' % artist

        raise Return(self._build_response(answer))

    def _get_speakers(self):
        speakers = yield self._speaker_list()
        if len(speakers) > 0:
            speaker_list = ', '.join([s['name'] for s in speakers])
            raise Return(self._build_response('I found these speakers: %s' % speaker_list))
        else:
            raise Return(self._build_response('Sorry, I couldn\'t find any speakers!', True))

    @coroutine
    def _speaker_list(self):
        response = yield self._request('sonos.speakers', {})

        result = response['result']
        if result['success'] is True:
            raise Return(result['speakers'])
        else:
            raise Return([])