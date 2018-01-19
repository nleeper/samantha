import config
import numbers

from tornado.gen import coroutine, Return

from base import BasePlugin
from clients.spotify import SpotifyClient

class Sonos(BasePlugin):
    def __init__(self, manager):
        BasePlugin.__init__(self, manager)

        self._spotify = SpotifyClient(config.SPOTIFY)

        self._intent_map = { 'play_genre': self._play_genre, 
                             'play_artist': self._play_artist, 
                             'play_playlist': self._play_playlist,
                             'play_album': self._play_album,
                             'play_track': self._play_track,
                             'speaker_list': self._get_speakers,
                             'pause_music': self._pause,
                             'resume_music': self._resume,
                             'skip_track': self._skip_track,
                             'volume': self._set_volume,
                             'currently_playing': self._currently_playing,
                             'playing_next': self._playing_next }
    
    @coroutine
    def handle(self, intent, entities):
        params = self._to_params(entities)
        return self._intent_map[intent](params)

    def _currently_playing(self, params):
        if not 'speaker' in params:
            speakers = yield self._speaker_list()
            raise Return(self._build_speaker_question('What speaker are you asking about?', speakers))

        answer = yield self._handle_request('sonos.speaker', 
                                            params, 
                                            lambda r: self._build_currently_playing_message(r['speaker']),
                                            lambda r: 'I couldn\'t find the speaker you asked about. Try again?')

        raise Return(self._build_response(answer))   

    def _build_currently_playing_message(self, speaker):
        state = speaker['state']
        name = speaker['name']

        playbackState = state.get('playbackState', 'STOPPED')
        if playbackState == 'PLAYING':
            return '\'%s\' by \'%s\' is currently playing on speaker %s' % (state['currentTrack']['title'], state['currentTrack']['artist'], name)
        elif playbackState == 'STOPPED':
            return 'Sorry, nothing is currently playing on speaker %s' % name
        elif playbackState == 'PAUSED_PLAYBACK':
            return 'Music is paused on speaker %s right now' % name 

    def _playing_next(self, params):
        if not 'speaker' in params:
            speakers = yield self._speaker_list()
            raise Return(self._build_speaker_question('What speaker are you asking about?', speakers))

        answer = yield self._handle_request('sonos.speaker', 
                                            params, 
                                            lambda r: self._build_playing_next_message(r['speaker']),
                                            lambda r: 'I couldn\'t find the speaker you asked about. Try again?')

        raise Return(self._build_response(answer))

    def _build_playing_next_message(self, speaker):
        state = speaker['state']
        name = speaker['name']

        nextTrack = state.get('nextTrack', {})
        nextTrackTitle = nextTrack.get('title', '')
        nextTrackArtist = nextTrack.get('artist', '')

        answer = ''
        playbackState = state.get('playbackState', 'STOPPED')
        if playbackState == 'PLAYING':
            if nextTrackTitle != '':
                answer = '\'%s\' by \'%s\' is going to play next on speaker %s' % (state['nextTrack']['title'], state['nextTrack']['artist'], name)
        elif playbackState == 'PAUSED_PLAYBACK':
            if nextTrackTitle != '':
                answer = 'Music is paused on speaker %s right now, but \'%s\' by \'%s\' is going to play next' % (name, state['nextTrack']['title'], state['nextTrack']['artist'])

        if answer == '':
            answer = 'Sorry, nothing is queued to play next on speaker %s' % name

        return answer

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
            current_volume = int(result['speaker']['state'].get('volume', 0))
            
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

        answer = yield self._handle_request('sonos.next',
                                            params,
                                            lambda r: 'Skipped ahead to the next song',
                                            lambda r: 'I was unable to skip this song. Sorry :(')

        raise Return(self._build_response(answer))

    def _resume(self, params):
        if not 'speaker' in params:
            speakers = yield self._speaker_list()
            raise Return(self._build_speaker_question('What speaker should I resume playing?', speakers))

        answer = yield self._handle_request('sonos.play',
                                            params,
                                            lambda r: 'Music is now playing :)',
                                            lambda r: 'I was unable to resume playing music. Sorry :(')

        raise Return(self._build_response(answer))

    def _pause(self, params):
        if not 'speaker' in params:
            speakers = yield self._speaker_list()
            raise Return(self._build_speaker_question('What speaker should I pause?', speakers))

        answer = yield self._handle_request('sonos.pause',
                                            params,
                                            lambda r: 'The music has been paused.',
                                            lambda r: 'I was unable to pause the music. Sorry :(')

        raise Return(self._build_response(answer))

    def _play_genre(self, params):
        if not 'genre' in params:
            raise Return(self._build_response('I don\'t know what genre you want me to play. Ask again?', True))

        genre = params['genre']
        del params['genre']

        if not 'speaker' in params:
            speakers = yield self._speaker_list()
            raise Return(self._build_speaker_question('What speaker do you want me to play genre \'%s\' on?' % genre.title(), speakers))

        found = self._spotify.find_random_playlist_for_genre(genre)
        if found is not None:
            params['uri'] = found['uri']

            answer = yield self._play_spotify(params,
                                              'The playlist \'%s\' is now playing. Hope you like it!' % found['name'],
                                              'I couldn\'t play the genre you wanted. Sorry!')
        else:
            answer = 'I couldn\'t find any playlists for genre \'%s\'. Try again?' % genre.title()

        raise Return(self._build_response(answer))

    def _play_playlist(self, params):
        if not 'playlist' in params:
            raise Return(self._build_response('I don\'t know what playlist you want me to play. Try again?', True))

        playlist = params['playlist']
        del params['playlist']
        
        if not 'speaker' in params:
            speakers = yield self._speaker_list()
            raise Return(self._build_speaker_question('What speaker do you want me to play playlist \'%s\' on?' % playlist.title(), speakers))

        found = self._spotify.find_playlist(playlist)
        if found is not None:
            params['uri'] = found['uri']

            answer = yield self._play_spotify(params,
                                              'Playlist \'%s\' is playing. Enjoy!' % found['name'],
                                              'I couldn\'t play the playlist you wanted. Sorry!')
        else:
            answer = 'I couldn\'t find the playlist \'%s\'. Try again?' % playlist.title()

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
            raise Return(self._build_speaker_question('What speaker do you want me to play album \'%s\' on?' % album.title(), speakers))

        found = self._spotify.find_album_by_artist(album, artist)
        if found is not None:
            params['uri'] = found['uri']

            answer = yield self._play_spotify(params,
                                              'Your album \'%s\' is playing. Enjoy!' % found['name'],
                                              'I couldn\'t play the album you wanted. Sorry!')
        else:
            answer = 'I couldn\'t find the album \'%s\' by artist \'%s\'. Try again?' % (album.title(), artist.title())

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
            raise Return(self._build_speaker_question('What speaker do you want me to play track \'%s\' on?' % track.title(), speakers))

        found = self._spotify.find_track_by_artist(track, artist)
        if found is not None:
            params['uri'] = found['uri']

            answer = yield self._play_spotify(params,
                                              'Your song \'%s\' is playing. Enjoy!' % found['name'],
                                              'I couldn\'t play the song you wanted. Sorry!')
        else:
            answer = 'I couldn\'t find the song \'%s\' by artist \'%s\'. Try again?' % (track.title(), artist.title())

        raise Return(self._build_response(answer))

    def _play_artist(self, params):
        if not 'artist' in params:
            raise Return(self._build_response('I don\'t know what artist you want me to play. Try again?', True))

        artist = params['artist']
        del params['artist']
        
        if not 'speaker' in params:
            speakers = yield self._speaker_list()
            raise Return(self._build_speaker_question('What speaker do you want me to play music by artist \'%s\' on?' % artist.title(), speakers))

        found = self._spotify.find_artist(artist)
        if found is not None:
            params['uri'] = 'spotify:artistTopTracks:%s' % found['id']

            answer = yield self._play_spotify(params,
                                              'Music by artist \'%s\' is playing. Enjoy!' % found['name'],
                                              'I couldn\'t play the artist you wanted. Sorry!')
        else:
            answer = 'I couldn\'t find the artist \'%s\'. Try again?' % artist.title()

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
    def _handle_request(self, method, params, success_func, fail_func):
        response = yield self._request(method, params)

        result = response['result']
        if result['success'] is True:
            raise Return(success_func(result))
        else:
            raise Return(fail_func(result))

    @coroutine
    def _play_spotify(self, params, success, fail):
        answer = yield self._handle_request('sonos.play_spotify', params, lambda r: success, lambda r: fail)
        raise Return(answer)

    @coroutine
    def _speaker_list(self):
        speakers = yield self._handle_request('sonos.speakers', {}, lambda r: r['speakers'], lambda r: [])
        raise Return(speakers)
