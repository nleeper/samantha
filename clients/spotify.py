
import random
import spotipy

from spotipy.oauth2 import SpotifyClientCredentials

class SpotifyClient(object):
    def __init__(self, options):
        self._spotipy = spotipy.Spotify(client_credentials_manager=
                                        SpotifyClientCredentials(client_id=options.get('CLIENT_ID'), 
                                                                 client_secret=options.get('CLIENT_SECRET')))

    def find_artist(self, artist):
        return self._top_search_match(artist, 'artist')

    def find_track_by_artist(self, track, artist):
        return self._top_search_match('track:%s artist:%s' % (track, artist), 'track')

    def find_album_by_artist(self, album, artist):
        return self._top_search_match('album:%s artist:%s' % (album, artist), 'album')

    def find_playlist(self, playlist):
        return self._top_search_match(playlist, 'playlist')

    def find_random_playlist_for_genre(self, genre):
        random_playlist = None

        found = self.search(genre, 'playlist', limit=50)
        if found['playlists']['total'] > 0:
            count = len(found['playlists']['items'])
            item_no = random.randint(0, count - 1)

            random_playlist = found['playlists']['items'][item_no]

        return random_playlist

    def search(self, name, search_type, limit=25):
        return self._spotipy.search(name, limit=limit, type=search_type, market='US')

    def _top_search_match(self, query, search_type, limit=10):
        plural_type = '%ss' % search_type
        found = self.search(query, search_type, limit=limit)
        return found[plural_type]['items'][0] if found[plural_type]['total'] > 0 else None