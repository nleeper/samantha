import os
import shutil

from rasa_nlu.converters import load_data
from rasa_nlu.config import RasaNLUConfig
from rasa_nlu.model import Trainer

rasa_config = RasaNLUConfig('config_spacy.json')

print 'Training new model from data %s' % rasa_config.data
training_data = load_data(rasa_config.data)
trainer = Trainer(rasa_config)
trainer.train(training_data)

print 'Persisting new model to %s' % rasa_config.path
new_model_dir = trainer.persist(rasa_config.path)

print 'Removing current model'
current_model_dir = os.path.join(rasa_config.path, 'current')
if os.path.isdir(current_model_dir):
    shutil.rmtree(current_model_dir)

print 'Moving new model to current model'
os.rename(new_model_dir, current_model_dir)

print 'Training complete!'