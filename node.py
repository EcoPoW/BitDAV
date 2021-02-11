#!/usr/bin/env python

"""tornado-webdav.py -- run a wsgidav server through tornado

This script requires tornado commit id
1ae186a504224e9f6cf5375b56f8e26e4774e2a0.  The easiest way to get this
patch is to clone the git repository and install using setup.py:

   git clone git://github.com/facebook/tornado.git
   cd tornado
   python setup.py develop

Command-line arguments are the same as for the wsgidav utility.  For
example:

   mkdir /tmp/dav
   tornado-dav.py -r /tmp/dav -p 8888
   ## Mount http://localhost:8888/ in your filesystem.

There is a problem PUTing files to the WebDAV server using Finder in
OS X; use the Terminal as a workaround.
"""

import os
import argparse
import sqlite3
import uuid

import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.wsgi
from wsgidav import wsgidav_app
from wsgidav.fs_dav_provider import FilesystemProvider

import ecdsa

import chain


def main():
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

    if not os.path.exists('%s.db' % current_name):
        conn = sqlite3.connect('%s.db' % current_name)
        c = conn.cursor()

        # Create table
        c.execute('''CREATE TABLE "chain" (
                "id"	INTEGER,
                "hash"	TEXT NOT NULL,
                "prev_hash"	TEXT NOT NULL,
                "height"	INTEGER NOT NULL,
                "timestamp"	INTEGER NOT NULL,
                "data"	TEXT NOT NULL,
                PRIMARY KEY("id" AUTOINCREMENT)
            )''')

        # Insert a row of data
        c.execute("INSERT INTO chain(hash, prev_hash, height, timestamp, data) VALUES (?, ?, 0, CURRENT_TIMESTAMP, '{}')", (uuid.uuid4().hex, uuid.uuid4().hex))

        # Save (commit) the changes
        conn.commit()

        # We can also close the connection if we are done with it.
        # Just be sure any changes have been committed or they will be lost.
        conn.close()


    sk_filename = "%s.pem" % current_name
    if os.path.exists(sk_filename):
        pass
    else:
        sk = ecdsa.SigningKey.generate(curve=ecdsa.NIST256p)
        open("./"+sk_filename, "w").write(bytes.decode(sk.to_pem()))


    #  config = wsgidav_app._initConfig()
    provider = FilesystemProvider('.')
    config = {
        "provider_mapping": {"/": provider},
        "http_authenticator": {
            "domain_controller": None  # None: dc.simple_dc.SimpleDomainController(user_mapping)
        },
        "simple_dc": {
            "user_mapping": {"*": True}
        },  # anonymous access
        "verbose": 1,
        "enable_loggers": [],
        "property_manager": True,  # True: use property_manager.PropertyManager
        "lock_manager": True,  # True: use lock_manager.LockManager
        "port": 8000
    }
    wsgi_app = wsgidav_app.WsgiDAVApp(config)
    settings = {"debug": True}
    application = tornado.web.Application([ (r'/\*gossip', chain.TestHandler),
                                            # (r'/*join_request', chain.TestHandler),
                                            # (r'/*join_approve', chain.TestHandler),
                                            (r'/\*leave', chain.TestHandler),
                                            (r'/\*invite', chain.TestHandler),
                                            (r'/\*get_block', chain.TestHandler),
                                            # ('/\*get_nodes', TestHandler),
                                            ('/\*test', chain.TestHandler),
            (r'.*', tornado.web.FallbackHandler, dict(fallback=tornado.wsgi.WSGIContainer(wsgi_app))),
        ], **settings)

    server = tornado.httpserver.HTTPServer(application)
    server.listen(config['port'])
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
