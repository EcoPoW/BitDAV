
import os
import argparse
import uuid
import time
import hashlib
import copy

import tornado.web
import tornado.httpclient
import tornado.escape

import ecdsa

import database

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
                for chain in chains:
                    prev_block = chain[-1]
                    prev_block_hash = prev_block[1]
                    # print(prev_block_hash)
                    if prev_block_hash == prev_hash:
                        forking_chain = copy.copy(chain)
                        # chain.append(leaf.hash)
                        chain.append(leaf)
                        chains.append(forking_chain)
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

def get_chain(reload=False):
    global chain_longest
    if reload or not chain_longest:
        chain_longest = longest_chain()
    return chain_longest
    # print(longest)

def latest_block_hash():
    global chain_longest
    if chain_longest:
        return chain_longest[-1][1]
    return '0'*64

def latest_block_height():
    global chain_longest
    if chain_longest:
        return chain_longest[-1][3]
    return 0

def update_chain(new_block_data):
    global chain_longest
    conn = database.get_conn()
    c = conn.cursor()

    block_hash = latest_block_hash()
    block_height = latest_block_height()
    new_block_data_json = tornado.escape.json_encode(new_block_data)
    digest = hashlib.sha256((block_hash+str(block_height)+new_block_data_json).encode('utf8'))
    new_block_hash = digest.hexdigest()

    c.execute("INSERT INTO chain(hash, prev_hash, height, timestamp, data) VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?)", (new_block_hash, block_hash, block_height+1, new_block_data_json))
    conn.commit()
    print(c.lastrowid)

    c.execute("SELECT * FROM chain WHERE id = ?", (c.lastrowid, ))
    block = c.fetchone()
    chain_longest.append(block)
    return block[1:]

@tornado.gen.coroutine
def broadcast_block(new_block):
    http_client = tornado.httpclient.AsyncHTTPClient()
    names, pirmary = get_names()
    for name, info in names.items():
        host, port, pk = info
        print('broadcast_block', host, port, name, new_block)
        if name == current_name:
            continue
        try:
            response = yield http_client.fetch("http://%s:%s/*gossip" % (host, port), method='POST', request_timeout=10, body=tornado.escape.json_encode(new_block))
        except:
            pass

@tornado.gen.coroutine
def ping():
    global failed_names
    global current_name
    global recent_election_block

    http_client = tornado.httpclient.AsyncHTTPClient()
    names, pirmary = get_names()
    all_names = sorted(list(names.keys()))
    failed_names = set()

    print('ping recent_block', recent_election_block)
    if current_name == pirmary and recent_election_block:
        print('ping broadcast', current_name, pirmary)
        # recent_block = get_chain()[-1]
        broadcast_block(list(recent_election_block[1:]))

    is_election_required = False
    for name, info in names.items():
        host, port, pk = info
        if name == current_name:
            pass
        try:
            response = yield http_client.fetch("http://%s:%s/*ping" % (host, port), request_timeout=1)
            print('ping', time.time(), host, port, response.request_time)
            if name in failed_names:
                failed_names.remove(name)
        except:
            print('ping failed', time.time(), host, port)
            failed_names.add(name)
            if name == pirmary:
                is_election_required = True

    if is_election_required:
        elected = get_elected(pirmary, all_names, failed_names)
        host, port, pk = names[elected]
        print('ping election', all_names, failed_names, pirmary)
        print('ping election', time.time(), elected, host, port)
        msg_json = tornado.escape.json_encode({'type': 'name', 'pirmary': elected, 'failed': list(failed_names), 'sig': {current_name: ''}})
        response = yield http_client.fetch("http://%s:%s/*election" % (host, port), method='POST', request_timeout=10, body=msg_json)

def get_elected(pirmary, all_names, failed_names):
    i = all_names.index(pirmary)
    while True:
        i += 1
        if i >= len(all_names):
            i = 0
        if all_names[i] not in failed_names:
            break
    return all_names[i]


def get_names(reload=False):
    global chain_names
    global recent_election_block

    pirmary = None
    if chain_names or not reload:
        chain_names = {}
        for block in get_chain():
            block_data_json = block[5]
            block_data = tornado.escape.json_decode(block_data_json)
            print('get_names', block_data)
            # print(names)
            if block_data.get('type') == 'name':
                if 'name' in block_data:
                    name = block_data['name']
                    host = block_data['host']
                    port = block_data['port']
                    pk = block_data['pk']
                    if name:
                        chain_names[name] = [host, port, pk]
                if 'pirmary' in block_data:
                    pirmary = block_data['pirmary']
                    recent_election_block = block
    print('get_names', chain_names, pirmary)
    return chain_names, pirmary


@tornado.gen.coroutine
def fetch_chain(host, port, block_hash):
    http_client = tornado.httpclient.AsyncHTTPClient()
    conn = database.get_conn()
    c = conn.cursor()
    while True:
        # try:
        response = yield http_client.fetch("http://%s:%s/*get_block?hash=%s" % (host, port, block_hash), request_timeout=10)
        rsp = tornado.escape.json_decode(response.body)
        block = rsp['block']
        block_height = block[2]

        c.execute("SELECT * FROM chain WHERE hash = ?", (block_hash,))
        blocks = c.fetchall()
        print('fetch_chain', block_hash, blocks)
        # if c.rowcount == 0:
        if not blocks:
            c.execute("INSERT INTO chain(hash, prev_hash, height, timestamp, data) VALUES (?, ?, ?, ?, ?)", tuple(block))

        if block_height == 1:
            break
        block_hash = block[1]
    conn.commit()
    get_chain(True)


# frozen_block_hash = None
chain_longest = None
# frozen_names = {}
recent_election_block = None
chain_names = None
failed_names = set()

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
print('parser', current_name, current_host, current_port)

conn = database.get_conn(current_name)
# c = conn.cursor()
# Insert a row of data
# c.execute("INSERT INTO chain(hash, prev_hash, height, timestamp, data) VALUES (?, ?, 0, CURRENT_TIMESTAMP, '{}')", (uuid.uuid4().hex, '0'*64))

# Save (commit) the changes
# conn.commit()

# c.execute("SELECT * FROM chain")
# for i in c.fetchall():
#     print(i)

sk_filename = "%s.pem" % current_name
if os.path.exists(sk_filename):
    current_sk = ecdsa.SigningKey.from_pem(open("./"+sk_filename).read())
else:
    current_sk = ecdsa.SigningKey.generate(curve=ecdsa.NIST256p)
    open("./"+sk_filename, "w").write(bytes.decode(current_sk.to_pem()))
print(current_sk)


names, pirmary = get_names()
update_host_or_port = False
if current_name in names:
    host, port, pk = names[current_name]
    if current_host is None:
        current_host = host
    else:
        if current_host != host:
            update_host_or_port = True

    if current_port is None:
        current_port = port
    else:
        if current_port != port:
            update_host_or_port = True
else:
    if current_host and current_port:
        update_host_or_port = True

if update_host_or_port:
    print('update_host_or_port', current_host, current_port)
    # tornado.ioloop.IOLoop.instance().add_callback(update_host_or_port_callback)
    block_data = {'type': 'name', 'name': current_name, 'host': current_host, 'port': current_port, 'timestamp': time.time(), 'pk': ''}
    if not pirmary:
        block_data['pirmary'] = current_name
    block = update_chain(block_data)
    get_names(True)
    broadcast_block(list(block))


ping_task = tornado.ioloop.PeriodicCallback(ping, 10000) # , jitter=0.5
ping_task.start()

messages = []


class TestHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('chain test')

class GoHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('chain test')

class ElectionHandler(tornado.web.RequestHandler):
    received_election = {}
    def post(self):
        global failed_names
        global recent_election_block

        names, pirmary = get_names()
        all_names = sorted(list(names.keys()))
        elected = get_elected(pirmary, all_names, failed_names)
        print('ElectionHandler', names, failed_names)
        print('ElectionHandler msg', self.request.body)

        msg = tornado.escape.json_decode(self.request.body)
        if 'sig' not in msg:
            raise
        node_name, sig = list(msg['sig'].items())[0]
        msg.pop('sig')
        msg_json = tornado.escape.json_encode(msg)

        block_data = {'type': 'name', 'pirmary': elected, 'failed': list(failed_names)}
        block_data_json = tornado.escape.json_encode(block_data)
        print('ElectionHandler own', block_data_json)
        assert msg_json == block_data_json

        self.received_election.setdefault(block_data_json, {})
        self.received_election[block_data_json][node_name] = sig
        print('ElectionHandler', self.received_election)
        assert set(self.received_election[block_data_json].keys()) == set(all_names) - failed_names

        assert set(msg['failed']) == failed_names
        block_data['sig'] = self.received_election[block_data_json]
        recent_election_block = update_chain(block_data)
        broadcast_block(list(recent_election_block))

        self.finish('')

class GossipHandler(tornado.web.RequestHandler):
    arrived_block_hash = set()
    def post(self):
        block_json = self.request.body
        block = tornado.escape.json_decode(block_json)
        assert isinstance(block, list)

        block_hash = block[0]
        prev_block_hash = block[1]
        if block_hash in self.arrived_block_hash:
            self.finish({})
            return

        conn = database.get_conn()
        c = conn.cursor()
        c.execute("SELECT * FROM chain WHERE hash = ?", (block_hash,))
        blocks = c.fetchall()
        # if c.rowcount == 0:
        is_fetch_required = False
        if not blocks:
            c.execute("INSERT INTO chain(hash, prev_hash, height, timestamp, data) VALUES (?, ?, ?, ?, ?)", tuple(block))
            conn.commit()
            print(c.lastrowid)
            self.arrived_block_hash.add(block_hash)

            # c.execute("SELECT * FROM chain WHERE id = ?", (c.lastrowid, ))
            # block = c.fetchone()
            if prev_block_hash == chain_longest[-1][1]:
                chain_longest.append([c.lastrowid]+block)
            else:
                is_fetch_required = True
                names, pirmary = get_names()
                host, port, pk = names[pirmary]

        # get host and port from the new pirmary
        block_data_json = block[4]
        block_data = tornado.escape.json_decode(block_data_json)
        print('GossipHandler', block_hash, block_data)
        if 'pirmary' in block_data:
            names, pirmary = get_names()
            print('GossipHandler', block_hash, names[block_data['pirmary']])
            host, port, pk = names[block_data['pirmary']]
            is_fetch_required = True

        if is_fetch_required:
            fetch_chain(host, port, block_hash)

        self.finish({})


class PingHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('pong')


# class JoinRequestHandler(tornado.web.RequestHandler):
#     def get(self):
#         self.finish('chain test')

#     def post(self):
#         self.finish('chain test')

# class JoinApproveHandler(tornado.web.RequestHandler):
#     def get(self):
#         self.finish('chain test')

#     def post(self):
#         self.finish('chain test')

class InviteHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('<form method="POST"><input name="addr"/><input type="submit" value="Invite"/></form>')

    @tornado.gen.coroutine
    def post(self):
        global messages
        addr = self.get_argument('addr')

        #fetch to get name and pk
        assert ':' in addr
        host, port = addr.split(':')
        req = {
                'host': current_host,
                'port': current_port,
                'highest_block_hash': latest_block_hash()
            }
        req_json = tornado.escape.json_encode(req)

        http_client = tornado.httpclient.AsyncHTTPClient()
        # try:
        response = yield http_client.fetch("http://%s:%s/*hello" % (host, port), method='POST', request_timeout=10, body=req_json)
        rsp = tornado.escape.json_decode(response.body)

        # need to check if the name already exists in the chain
        block_data = {'type': 'name', 'name': rsp['name'], 'host': host, 'port': port, 'timestamp': time.time(), 'pk': ''}
        block = update_chain(block_data)
        broadcast_block(list(block))

        self.finish({'addr':addr, 'messages': messages, 'name': rsp['name']})

        # except:
        #     pass


class LeaveHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('<form method="POST"><input type="submit" value="Leave"/></form>')

    def post(self):
        self.finish('leave test')

class HelloHandler(tornado.web.RequestHandler):
    def get(self):
        self.post()

    # @tornado.gen.coroutine
    def post(self):
        req = tornado.escape.json_decode(self.request.body)
        host = req['host']
        port = req['port']
        block_hash = req['highest_block_hash']
        self.finish({'name': current_name, 'pk': ''})
        fetch_chain(host, port, block_hash)


class GetBlockHandler(tornado.web.RequestHandler):
    def get(self):
        block_hash = self.get_argument('hash')

        conn = database.get_conn()
        c = conn.cursor()
        c.execute("SELECT * FROM chain WHERE hash = ?", (block_hash, ))
        block = c.fetchone()
        print('GetBlockHandler', block)

        self.finish({'block': list(block[1:])})


class TestShutdownHandler(tornado.web.RequestHandler):
    def get(self):
        pass
        tornado.ioloop.IOLoop.instance().stop()
