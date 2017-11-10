from rasa_nlu.model import Metadata, Interpreter
from rasa_nlu.config import RasaNLUConfig

class MessageParser(object):
    def __init__(self):
        self._metadata = Metadata.load('./models/current')
        self._interpreter = Interpreter.load(self._metadata, RasaNLUConfig('config_spacy.json'))

    def parse(self, message):
        response = { 'original': message, 'intent': None, 'entities': [] }

        parsed = self._interpreter.parse(message)
        # print parsed

        if parsed['intent'].get('confidence', 0.00) > 0.30:
            response['intent'] = parsed['intent'].get('name', '')
        if len(parsed['entities']) > 0:
            for e in parsed['entities']:
                response['entities'].append({ 'value': e['value'], 'entity': e['entity'] })

        return response
