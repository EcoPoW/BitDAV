
import tornado.web


messages = []

class TestHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('chain test')


class GossipHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('chain test')

    def post(self):
        self.finish('chain test')


class JoinRequestHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('chain test')

    def post(self):
        self.finish('chain test')

class JoinApproveHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('chain test')

    def post(self):
        self.finish('chain test')
