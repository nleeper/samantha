
class Sonos(object):
    def __init__(self):
        self._intent_map = { 'play_artist': 'sonos.play', 'speaker_list': 'sonos.speakers' }

    def supported_intents(self):
        return list(self._intent_map.keys())

    def to_action(self, intent, entities):
        return { 'method': self._intent_map[intent], 'params': entities }