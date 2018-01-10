import json
import spotipy
import config
import random
import numbers

from tornado.gen import coroutine, Return
from spotipy.oauth2 import SpotifyClientCredentials

from base import BasePlugin

class Sonos(BasePlugin):
    def __init__(self, manager):
        BasePlugin.__init__(self, manager)

        self._spotify = spotipy.Spotify(client_credentials_manager=
                                        SpotifyClientCredentials(client_id=config.SPOTIFY.get('CLIENT_ID'), 
                                                                 client_secret=config.SPOTIFY.get('CLIENT_SECRET')))

        self._intent_map = { 'play_genre': self._play_genre, 
                             'play_artist': self._play_artist, 
                             'speaker_list': self._get_speakers,
                             'pause_music': self._pause,
                             'resume_music': self._resume,
                             'skip_track': self._skip_track,
                             'play_album': self._play_album,
                             'play_track': self._play_track,
                             'volume': self._set_volume }
    
    @coroutine
    def handle(self, intent, entities):
        params = self._to_params(entities)
        return self._intent_map[intent](params)

    def _set_volume(self, params):
        if not 'direction' in params:
            raise Return(self._build_response('I don\'t know whether to turn the volume up or down. Ask again?', True))

        if not 'speaker' in params:
            speakers = yield self._speaker_list()
            raise Return(self._build_speaker_question('What speaker should change the volume on?', speakers))

        direction = params['direction'].lower()
        if params['direction'] not in ['up', 'down']:
            raise Return(self._build_response('I can only turn the volume up or down. Try asking again?', True))

        del params['direction']

        amount = 10
        if 'amount' in params:
            amount_map = { 'bit': 5, 'little': 10, 'lot': 20 }
            amount_value = params['amount'].replace('%', '').lower()

            del params['amount']
            
            if amount_value in amount_map:
                amount = amount_map[amount_value]
            elif isinstance(amount_value, numbers.Integral):
                amount = int(amount_value)      

        response = yield self._request('sonos.speaker', params)

        result = response['result']
        if result['success'] is True:
            current_volume = result['speaker']['state'].get('volume', 0)
            
            if direction == 'up':
                new_volume = current_volume + amount
            elif direction == 'down':
                new_volume = current_volume - amount

            params['level'] = new_volume
            vol_response = yield self._request('sonos.volume', params)

            vol_result = vol_response['result']
            if vol_result['success'] is True:
                answer = 'I changed the volume for you!'
            else:
                answer = 'Oh no, I couldn\'t change the volume. Sorry :('
        else:
            answer = 'I couldn\'t find the speaker you wanted to change the volume on. Try again?'

        raise Return(self._build_response(answer))

    def _skip_track(self, params):
        if not 'speaker' in params:
            speakers = yield self._speaker_list()
            raise Return(self._build_speaker_question('What speaker should I skip to the next song on?', speakers))

        response = yield self._request('sonos.next', params)

        result = response['result']
        if result['success'] is True:
            answer = 'Skipped ahead to the next song!'
        else:
            answer = 'I was unable to skip this song. Sorry :('

        raise Return(self._build_response(answer))

    def _resume(self, params):
        if not 'speaker' in params:
            speakers = yield self._speaker_list()
            raise Return(self._build_speaker_question('What speaker should I resume playing?', speakers))

        response = yield self._request('sonos.play', params)

        result = response['result']
        if result['success'] is True:
            answer = 'Music is now playing :)'
        else:
            answer = 'I was unable to resume playing music. Sorry :('

        raise Return(self._build_response(answer))

    def _pause(self, params):
        if not 'speaker' in params:
            speakers = yield self._speaker_list()
            raise Return(self._build_speaker_question('What speaker should I pause?', speakers))

        response = yield self._request('sonos.pause', params)

        result = response['result']
        if result['success'] is True:
            answer = 'The music has been paused.'
        else:
            answer = 'I was unable to pause the music. Sorry :('

        raise Return(self._build_response(answer))

    def _play_genre(self, params):
        if not 'genre' in params:
            raise Return(self._build_response('I don\'t know what genre you want me to play. Ask again?', True))

        genre = params['genre']
        del params['genre']

        if not 'speaker' in params:
            speakers = yield self._speaker_list()
            raise Return(self._build_speaker_question('What speaker do you want me to play %s on?' % genre.title(), speakers))

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
            answer = 'I couldn\'t find any playlists for genre %s. Try again?' % genre.title()

        raise Return(self._build_response(answer))

    def _play_album(self, params):
        if not 'album' in params:
            raise Return(self._build_response('I don\'t know what album you want me to play. Ask again?', True))

        if not 'artist' in params:
            raise Return(self._build_response('You need to tell me which artist made this album so I cand find it for you.', True))

        album = params['album']
        del params['album']

        artist = params['artist']
        del params['artist']

        if not 'speaker' in params:
            speakers = yield self._speaker_list()
            raise Return(self._build_speaker_question('What speaker do you want me to play %s on?' % album.title(), speakers))

        found = self._spotify.search('album:%s artist:%s' % (album, artist), limit=10, type='album', market='us')
        if found['albums']['total'] > 0:
            match = found['albums']['items'][0]
            params['uri'] = match['uri']

            response = yield self._request('sonos.play_spotify', params)

            result = response['result']
            if result['success'] is True:
                answer = 'Your album %s is playing. Enjoy!' % match['name']
            else:
                answer = 'I couldn\'t play the album you wanted. Sorry!'
        else:
            answer = 'I couldn\'t find the album %s by artist %s. Try again?' % (album.title(), artist.title())

        raise Return(self._build_response(answer))

    def _play_track(self, params):
        if not 'track' in params:
            raise Return(self._build_response('I don\'t know what song you want me to play. Ask again?', True))

        if not 'artist' in params:
            raise Return(self._build_response('You need to tell me which artist made this song so I cand find it for you.', True))

        track = params['track']
        del params['track']

        artist = params['artist']
        del params['artist']

        if not 'speaker' in params:
            speakers = yield self._speaker_list()
            raise Return(self._build_speaker_question('What speaker do you want me to play %s on?' % track.title(), speakers))

        found = self._spotify.search('track:%s artist:%s' % (track, artist), limit=10, type='track', market='us')
        if found['tracks']['total'] > 0:
            match = found['tracks']['items'][0]
            params['uri'] = match['uri']

            response = yield self._request('sonos.play_spotify', params)

            result = response['result']
            if result['success'] is True:
                answer = 'Your song %s is playing. Enjoy!' % match['name']
            else:
                answer = 'I couldn\'t play the song you wanted. Sorry!'
        else:
            answer = 'I couldn\'t find the song %s by artist %s. Try again?' % (track.title(), artist.title())

        raise Return(self._build_response(answer))

    def _play_artist(self, params):
        if not 'artist' in params:
            raise Return(self._build_response('I don\'t know what artist you want me to play. Try again?', True))

        artist = params['artist']
        del params['artist']
        
        if not 'speaker' in params:
            speakers = yield self._speaker_list()
            raise Return(self._build_speaker_question('What speaker do you want me to play %s on?' % artist.title(), speakers))

        found = self._spotify.search(artist, limit=10, type='artist', market='US')
        if found['artists']['total'] > 0:
            match = found['artists']['items'][0]
            params['uri'] = 'spotify:artistTopTracks:%s' % match['id']

            response = yield self._request('sonos.play_spotify', params)
            
            result = response['result']
            if result['success'] is True:
                answer = 'Songs by artist %s is playing. Enjoy!' % match['name']
            else:
                answer = 'I couldn\'t play the artist you wanted. Sorry!'
        else:
            answer = 'I couldn\'t find the artist %s. Try again?' % artist.title()

        raise Return(self._build_response(answer))

    def _get_speakers(self, params):
        speakers = yield self._speaker_list()
        if len(speakers) > 0:
            speaker_list = ', '.join([s['name'] for s in speakers])
            raise Return(self._build_response('I found these speakers: %s' % speaker_list))
        else:
            raise Return(self._build_response('Sorry, I couldn\'t find any speakers!', True))

    def _build_speaker_question(self, question, speakers):
        choices = [{ 'key': s['name'], 'value': s['name'] } for s in speakers]
        return self._build_question(question, 'speaker', choices=choices)

    @coroutine
    def _speaker_list(self):
        response = yield self._request('sonos.speakers', {})

        result = response['result']
        if result['success'] is True:
            raise Return(result['speakers'])
        else:
            raise Return([])