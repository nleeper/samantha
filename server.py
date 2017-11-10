import config

import tornado.ioloop
import tornado.web

from application import WebApplication
from clients.facebook import FacebookMessenger

# Start server
if __name__ == '__main__':
    app = WebApplication()
    app.initialize()

    tornado.ioloop.IOLoop.instance().add_callback(app.chat_processor.process)

    app.listen(config.PORT)

    print "Listening on port %s" % config.PORT

    tornado.ioloop.IOLoop.instance().start()