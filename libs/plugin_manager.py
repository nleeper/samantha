import tornado.gen

from plugins import PluginList

class PluginManager(object):
    def __init__(self, pipeline_manager):
        self._pipeline_manager = pipeline_manager
        
        self._intents = {}
        for P in PluginList:
            plugin = P(self)
            for i in plugin.supported_intents():
                self._intents[i] = plugin

    @property
    def pipeline(self):
        return self._pipeline_manager
    
    @tornado.gen.coroutine
    def handle(self, intent, entities):
        response = yield tornado.gen.maybe_future(self._intents[intent].handle(intent, entities))
        raise tornado.gen.Return(response)