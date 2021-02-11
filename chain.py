
import os
import argparse
import uuid
import time

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

conn = database.get_conn(current_name)
# database.get_conn()
c = conn.cursor()
# Insert a row of data
# c.execute("INSERT INTO chain(hash, prev_hash, height, timestamp, data) VALUES (?, ?, 0, CURRENT_TIMESTAMP, '{}')", (uuid.uuid4().hex, '0'*64))

# Save (commit) the changes
# conn.commit()

# c.execute("SELECT * FROM chain")
# for i in c.fetchall():
#     print(i)

sk_filename = "%s.pem" % current_name
if os.path.exists(sk_filename):
    sk = ecdsa.SigningKey.from_pem(open("./"+sk_filename).read())
else:
    sk = ecdsa.SigningKey.generate(curve=ecdsa.NIST256p)
    open("./"+sk_filename, "w").write(bytes.decode(sk.to_pem()))
print(sk)

def longest_chain(from_hash = '0'*64):
    conn = database.get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM chain WHERE prev_hash = ?", (from_hash,))
    roots = c.fetchall()

    chains = []
    prev_hashs = []
    for root in roots:
        # chains.append([root.hash])
        chains.append([root])
        # print(root)
        block_hash = root[1]
        prev_hashs.append(block_hash)

    t0 = time.time()
    n = 0
    while True:
        if prev_hashs:
            prev_hash = prev_hashs.pop(0)
        else:
            break

        c.execute("SELECT * FROM chain WHERE prev_hash = ?", (prev_hash,))
        leaves = c.fetchall()
        n += 1
        if len(leaves) > 0:
            block_height = leaves[0][3]
            if block_height % 1000 == 0:
                print('longest height', block_height)
            for leaf in leaves:
                for c in chains:
                    prev_block = c[-1]
                    prev_block_hash = prev_block[2]
                    if prev_block_hash == prev_hash:
                        chain = copy.copy(c)
                        # chain.append(leaf.hash)
                        chain.append(leaf)
                        chains.append(chain)
                        break
                leaf_hash = leaf[1]
                if leaf_hash not in prev_hashs and leaf_hash:
                    prev_hashs.append(leaf_hash)
    t1 = time.time()
    # print(tree.current_port, "query time", t1-t0, n)

    longest = []
    for i in chains:
        # print(i)
        if not longest:
            longest = i
        if len(longest) < len(i):
            longest = i
    return longest

chain = longest_chain()
print(chain)
highest_block_hash = None
if chain:
    highest_block_hash = chain[0][1]
print(highest_block_hash)

messages = []



class TestHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('chain test')


class GossipHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('chain test')

    def post(self):
        msg_json = self.request.body
        msg = json.loads(msg_json)
        assert isinstance(msg, dict)
        self.finish(msg)


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

        #fetch to get name and pk

        conn = database.get_conn()
        c = conn.cursor()
        c.execute("INSERT INTO chain(hash, prev_hash, height, timestamp, data) VALUES (?, ?, 0, CURRENT_TIMESTAMP, '{}')", (uuid.uuid4().hex, uuid.uuid4().hex))
        conn.commit()

        self.finish({'addr':addr, 'messages': messages})

class LeaveHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('<form method="POST"><input type="submit" value="Leave"/></form>')

    def post(self):
        self.finish('leave test')
