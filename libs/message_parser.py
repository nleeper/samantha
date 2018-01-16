import os
import json

import config

from rasa_nlu.model import Metadata, Interpreter
from rasa_nlu.config import RasaNLUConfig

class MessageParser(object):
    def __init__(self):
        self._metadata = Metadata.load('./models/current')
        self._interpreter = Interpreter.load(self._metadata, RasaNLUConfig(config.NLU_CONFIG))

    def parse(self, message):
        trimmed = message.strip().lower()

        response = { 'original': trimmed, 'intent': None, 'entities': [] }

        parsed = self._interpreter.parse(trimmed)
        if parsed['intent'].get('confidence', 0.00) > 0.30:
            response['intent'] = parsed['intent'].get('name', '')

            if len(parsed['entities']) > 0:
                for e in parsed['entities']:
                    response['entities'].append({ 'value': e['value'], 'entity': e['entity'] })
        else:
            print('Unable to find intent with 30%% confidence for message \'%s\' - %s' % (trimmed, parsed))

        self._log(trimmed, parsed)

        return response

    def _log(self, message, parsed):
        directory = config.NLU_LOG_DIR

        if not os.path.exists(directory):
            os.makedirs(directory)

        with open('%s/nlu.log' % directory, 'a') as outfile:
            json.dump({ 'original': message, 'parsed': parsed }, outfile)
            outfile.write('\n')
