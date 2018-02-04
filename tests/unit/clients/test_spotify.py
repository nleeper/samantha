from mock import Mock

from base import BaseTestCase

from clients.spotify import SpotifyClient

class TestSpotifyClient(BaseTestCase):

    default_opts = { 'CLIENT_ID': 'client_id',
                     'CLIENT_SECRET': 'client_secret' }

    def setUp(self):
        self.random_mock = self.mock('clients.spotify.random')
        self.spotipy_mock = self.mock('clients.spotify.Spotify')
        self.client_creds_mock = self.mock('clients.spotify.SpotifyClientCredentials')

        self.search_mock = Mock()
        self.spotipy_mock.return_value.search = self.search_mock

        self.spotify = SpotifyClient(self.default_opts)

    def testConstructor(self):
        self.client_creds_mock.assert_called_once_with(client_id=self.default_opts.get('CLIENT_ID'),
                                                       client_secret=self.default_opts.get('CLIENT_SECRET'))

        self.spotipy_mock.assert_called_once_with(client_credentials_manager=self.client_creds_mock.return_value)

    def testFindArtist(self):
        artist = 'Elvis Presley'
        result = { 'name': artist }

        results = { 'artists': { 'total': 1, 'items': [result] } }
        self.search_mock.return_value = results

        found_artist = self.spotify.find_artist(artist)

        self.search_mock.assert_called_once_with(artist, limit=10, type='artist', market='US')
        self.assertEqual(found_artist, result)

    def testFindArtistReturnNoneIfNoMatch(self):
        artist = 'The Beatles'

        results = { 'artists': { 'total': 0, 'items': [] } }
        self.search_mock.return_value = results

        found_artist = self.spotify.find_artist(artist)

        self.search_mock.assert_called_once_with(artist, limit=10, type='artist', market='US')
        self.assertIsNone(found_artist)

    def testFindTrackByArtist(self):
        track = 'Suspicious Minds'
        artist = 'Elvis Presley'
        result = { 'name': track, 'artist': artist }

        results = { 'tracks': { 'total': 1, 'items': [result] } }
        self.search_mock.return_value = results

        found_track = self.spotify.find_track_by_artist(track, artist)

        self.search_mock.assert_called_once_with('track:%s artist:%s' % (track, artist), limit=10, type='track', market='US')
        self.assertEqual(found_track, result)

    def testFindTrackByArtistReturnNoneIfNoMatch(self):
        track = 'Yellow Submarine'
        artist = 'The Beatles'

        results = { 'tracks': { 'total': 0, 'items': [] } }
        self.search_mock.return_value = results

        found_track = self.spotify.find_track_by_artist(track, artist)

        self.search_mock.assert_called_once_with('track:%s artist:%s' % (track, artist), limit=10, type='track', market='US')
        self.assertIsNone(found_track)

    def testFindAlbumByArtist(self):
        album = 'Elvis Now'
        artist = 'Elvis Presley'
        result = { 'name': album, 'artist': artist }

        results = { 'albums': { 'total': 1, 'items': [result] } }
        self.search_mock.return_value = results

        found_album = self.spotify.find_album_by_artist(album, artist)

        self.search_mock.assert_called_once_with('album:%s artist:%s' % (album, artist), limit=10, type='album', market='US')
        self.assertEqual(found_album, result)

    def testFindAlbumByArtistReturnNoneIfNoMatch(self):
        album = 'Abbey Road'
        artist = 'The Beatles'

        results = { 'albums': { 'total': 0, 'items': [] } }
        self.search_mock.return_value = results

        found_album = self.spotify.find_album_by_artist(album, artist)

        self.search_mock.assert_called_once_with('album:%s artist:%s' % (album, artist), limit=10, type='album', market='US')
        self.assertIsNone(found_album)

    def testFindPlaylist(self):
        playlist = 'ThrowbackThursday'
        result = { 'name': playlist }

        results = { 'playlists': { 'total': 1, 'items': [result] } }
        self.search_mock.return_value = results

        found_playlist = self.spotify.find_playlist(playlist)

        self.search_mock.assert_called_once_with(playlist, limit=10, type='playlist', market='US')
        self.assertEqual(found_playlist, result)

    def testFindPlaylistReturnNoneIfNoMatch(self):
        playlist = 'Celebrate'

        results = { 'playlists': { 'total': 0, 'items': [] } }
        self.search_mock.return_value = results

        found_playlist = self.spotify.find_playlist(playlist)

        self.search_mock.assert_called_once_with(playlist, limit=10, type='playlist', market='US')
        self.assertIsNone(found_playlist)

    def testFindRandomPlaylistForGenre(self):
        genre = 'Pop'
        result = { 'name': 'The best Pop playlist' }

        results = { 'playlists': { 'total': 1, 'items': [result] } }
        self.search_mock.return_value = results

        self.random_mock.randint.return_value = 0

        found_playlist = self.spotify.find_random_playlist_for_genre(genre)

        self.random_mock.randint.assert_called_once_with(0, 0)
        self.search_mock.assert_called_once_with(genre, limit=50, type='playlist', market='US')
        self.assertEqual(found_playlist, result)

    def testFindRandomPlaylistForGenreReturnNoneIfNoMatch(self):
        genre = 'Christmas'

        results = { 'playlists': { 'total': 0, 'items': [] } }
        self.search_mock.return_value = results

        found_playlist = self.spotify.find_random_playlist_for_genre(genre)

        self.search_mock.assert_called_once_with(genre, limit=50, type='playlist', market='US')
        self.assertIsNone(found_playlist)

    def testSearch(self):
        term = 'Mine'
        search_type = 'artist'

        results = { 'playlists': { 'total': 0, 'items': [] } }
        self.search_mock.return_value = results

        found = self.spotify.search(term, search_type)

        self.search_mock.assert_called_once_with(term, limit=25, type=search_type, market='US')
        self.assertEqual(found, results)

