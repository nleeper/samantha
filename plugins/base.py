class BasePlugin(object):
    def __init__(self, manager):
        self._manager = manager
        self._intent_map = {}

    def supported_intents(self):
        return list(self._intent_map.keys())

    def _request(self, method, params):
        return self._manager.pipeline.send_request_response(method, params)

    def _to_params(self, entities):
        return {e['entity']: e['value'] for e in entities}
    
    def _build_question(self, question, entity, choices=[]):
        question = { 'message': question, 'type': 'question', 'question_entity': entity } 
        if len(choices) > 0:
            question['choices'] = choices
        return question

    def _build_response(self, message, is_error = False):
        return { 'message': message, 'type': 'error' if is_error else 'response' }