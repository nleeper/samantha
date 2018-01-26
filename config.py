from decouple import config
from decouple import Csv

PORT = config('PORT', default=8888, cast=int)

NLU_CONFIG = config('NLU_CONFIG', default='config_spacy.json', cast=str)

NLU_LOG_DIR = config('NLU_LOG_DIR', default='logs', cast=str)

MIN_PARSE_CONFIDENCE = config('MIN_PARSE_CONFIDENCE', default=0.30, cast=float)

FACEBOOK = {
    'PAGE_ACCESS_TOKEN': config('FB_PAGE_ACCESS_TOKEN', default=''),
    'VERIFY_TOKEN': config('FB_VERIFY_TOKEN', default=''),
    'VALID_SENDER_IDS': config('FB_VALID_SENDER_IDS', default='', cast=Csv())
}

SPOTIFY = {
    'CLIENT_ID': config('SPOTIFY_CLIENT_ID', default=''),
    'CLIENT_SECRET': config('SPOTIFY_CLIENT_SECRET', default='')
}