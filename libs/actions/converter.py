
import imp
import os

from plugins import PluginList

PluginFolder = './libs/actions/plugins'

class ActionConverter(object):
    def __init__(self):
        self._intent_to_plugin = {}
        for p in PluginList:
            for i in p.supported_intents():
                self._intent_to_plugin[i] = p

    def convert(self, intent, entities):
        return self._intent_to_plugin[intent].to_action(intent, entities)