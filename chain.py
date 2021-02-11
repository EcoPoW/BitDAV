
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

class InviteHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('<form method="POST"><input name="addr"/><input type="submit" value="Invite"/></form>')

    def post(self):
        global messages
        addr = self.get_argument('addr')
        self.finish({'addr':addr, 'messages': messages})

class LeaveHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('<form method="POST"><input type="submit" value="Leave"/></form>')

    def post(self):
        self.finish('leave test')
