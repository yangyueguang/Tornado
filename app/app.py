#! /usr/bin/env python
# coding: utf-8

from tornado import httpserver, ioloop, web
import conf
import redis
from service.routes import routes


class Application(web.Application):
    def __init__(self):
        web.Application.__init__(self, routes, **conf.settings)
        self.redisdb = redis.StrictRedis(**conf.REDIS_CONF)


def start():
    application = Application()
    http_server = httpserver.HTTPServer(application)
    http_server.listen(conf.TORNADO_LISTEN_PORT)
    http_server.start(0)
    ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    start()
