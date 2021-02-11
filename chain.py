
import os
import argparse
import uuid

import tornado.web

import ecdsa

import database

parser = argparse.ArgumentParser(description="node description")
parser.add_argument('--name')
parser.add_argument('--host', default=None)
parser.add_argument('--port', default=None)
# parser.add_argument('--parent_host', default="127.0.0.1")
# parser.add_argument('--parent_port', default=2018)
# parser.add_argument('--control_host')
# parser.add_argument('--control_port', default=setting.DASHBOARD_PORT)

args = parser.parse_args()
current_name = args.name
current_host = args.host
current_port = args.port
print(current_name, current_host, current_port)
database.get_conn(current_name)
# database.get_conn()

sk_filename = "%s.pem" % current_name
if os.path.exists(sk_filename):
    pass
else:
    sk = ecdsa.SigningKey.generate(curve=ecdsa.NIST256p)
    open("./"+sk_filename, "w").write(bytes.decode(sk.to_pem()))


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
