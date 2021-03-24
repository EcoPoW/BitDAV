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

import tornado.web
import tornado.httpserver
import tornado.ioloop
import tornado.wsgi

# from wsgidav import wsgidav_app
# from wsgidav.fs_dav_provider import FilesystemProvider


import chain
import fs


def main():
    # provider = FilesystemProvider('.')
    # config = {
    #     "provider_mapping": {"/": provider},
    #     "http_authenticator": {
    #         "domain_controller": None  # None: dc.simple_dc.SimpleDomainController(user_mapping)
    #     },
    #     "simple_dc": {
    #         "user_mapping": {"*": True}
    #     },  # anonymous access
    #     "verbose": 1,
    #     "enable_loggers": [],
    #     "property_manager": True,  # True: use property_manager.PropertyManager
    #     "lock_manager": True,  # True: use lock_manager.LockManager
    #     # "port": 8000
    # }
    # wsgi_app = wsgidav_app.WsgiDAVApp(config)
    settings = {"debug": True}
    application = tornado.web.Application([ (r'/\*gossip', chain.GossipHandler),
                                            (r'/\*hello', chain.HelloHandler),
                                            (r'/\*ping', chain.PingHandler),
                                            (r'/\*election', chain.ElectionHandler),
                                            (r'/\*get_block', chain.GetBlockHandler),
                                            (r'/\*invite', chain.InviteHandler),
                                            (r'/\*go', chain.GoHandler),
                                            (r'/\*test_shutdown', chain.TestShutdownHandler),
                                            # (r'/\*leave', chain.LeaveHandler),
                                            # (r'/\*join_request', chain.JoinRequestHandler),
                                            # (r'/\*join_approve', chain.JoinApproveHandler),
                                            # (r'/\*get_nodes', TestHandler),

                                            (r'/\*get_folder', fs.GetFolderHandler),
                                            (r'/\*add_folder', fs.AddFolderHandler),
                                            (r'/\*update_folder', fs.UpdateFolderHandler),
                                            (r'/\*remove_folder', fs.RemoveFolderHandler),
                                            (r'/\*get_meta', fs.GetMetaHandler),
                                            # (r'/\*add_storage', fs.AddStorageHandler),
                                            (r'/\*update_storage', fs.UpdateStorageHandler),

                                            (r'/\*test', chain.TestHandler),
            # (r'.*', tornado.web.FallbackHandler, dict(fallback=tornado.wsgi.WSGIContainer(wsgi_app))),
        ], **settings)

    server = tornado.httpserver.HTTPServer(application)
    server.listen(chain.current_port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    print('node __main__', chain.current_name, chain.current_host, chain.current_port)
    main()
