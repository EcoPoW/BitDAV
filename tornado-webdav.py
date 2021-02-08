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

from tornado import httpserver, ioloop, wsgi
from wsgidav.server import run_server

def run():
    config = run_server._initConfig()
    app = run_server.WsgiDAVApp(config)
    server = httpserver.HTTPServer(wsgi.WSGIContainer(app))
    server.listen(config['port'])
    ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    run()
