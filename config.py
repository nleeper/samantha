from decouple import config
from decouple import Csv

PORT = config('PORT', default=8888, cast=int)

NLU_CONFIG = config('NLU_CONFIG', default='config_mitie.json', cast=str)

NLU_LOG_DIR = config('NLU_LOG_DIR', default='logs', cast=str)

FACEBOOK = {
    'PAGE_ACCESS_TOKEN': config('FB_PAGE_ACCESS_TOKEN', default=''),
    'VERIFY_TOKEN': config('FB_VERIFY_TOKEN', default=''),
    'VALID_SENDER_IDS': config('FB_VALID_SENDER_IDS', default='', cast=Csv())
}