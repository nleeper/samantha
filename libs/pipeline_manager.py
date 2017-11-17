import uuid
import json

from tornado.concurrent import Future

class PipelineManager(object):
    def __init__(self):
        self._id = str(uuid.uuid4())
        self._connection = None
        self._waiters = {}

    def set_connection(self, conn):
        if self._connection is not None:
            print "Pipeline connection is already being handled"
            return

        conn.id = self._id
        conn.stream.set_nodelay(True)

        self._connection = conn

    def reset(self):
        self._connection = None

    def handle_message(self, message):
        parsed_message = json.loads(message)
        if 'id' in parsed_message:
            # This is a response to a request
            id = parsed_message['id']
            if id in self._waiters:
                waiter = self._waiters[id]
                waiter.set_result(parsed_message)
                del self._waiters[id]
            else:
                print "Nobody waiting for response %s" % id
        else:
            print parsed_message['method']

    def send_request_response(self, method, params = None):
        message_id = str(uuid.uuid4())

        future = Future()
        self._waiters[message_id] = future
        self._send_message({ "id": message_id, "method": method, "params": params })
        return future

    def send_request(self, method, params = None):
        message_id = str(uuid.uuid4())
        return self._send_message({ "id": message_id, "method": method, "params": params })

    def send_response(self, message_id, result, error = None):
        return self._send_message({ "id": message_id, "result": result, "error": error })

    def send_notification(self, method):
        return self._send_message({ "id": None, "method": method })

    def _send_message(self, msg_dict):
        msg_dict["jsonrpc"] = "2.0"
        return self._connection.write_message(json.dumps(msg_dict))