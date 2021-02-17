
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
import chain

folder_names = {}
def get_folders(reload=False):
    global folder_names
    pirmary = None
    if folder_names or not reload:
        folder_names = {}
        for block in chain.get_chain():
            block_data_json = block[5]
            block_data = tornado.escape.json_decode(block_data_json)
            print('get_folders', block_data)
            # print(names)
            if block_data.get('type') == 'folder':
                # if 'name' in block_data:
                name = block_data['name']
                # meta_hash = block_data['hash']
                # update_time = block_data['update_time']
                # if name:
                folder_names[name] = ''#[items, update_time]
    print('get_folders', folder_names)
    return folder_names


class TestHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('chain test')


class AddFolderHandler(tornado.web.RequestHandler):
    def get(self):
        names = get_folders()
        self.write('<br>')
        self.write(names)
        self.write('<br>')
        self.finish('<form method="POST"><input name="folder"/><input type="submit" value="Add"/></form>')

    @tornado.gen.coroutine
    def post(self):
        folder_name = self.get_argument('folder')

        #fetch to get name and pk
        # assert ':' in addr
        # host, port = addr.split(':')
        # req = {
        #         'host': current_host,
        #         'port': current_port,
        #         'highest_block_hash': latest_block_hash()
        #     }
        # req_json = tornado.escape.json_encode(req)

        # http_client = tornado.httpclient.AsyncHTTPClient()
        # try:
        # response = yield http_client.fetch("http://%s:%s/*hello" % (host, port), method='POST', request_timeout=10, body=req_json)
        # rsp = tornado.escape.json_decode(response.body)

        # need to check if the name already exists in the chain
        block_data = {'type': 'folder', 'name': folder_name, 'timestamp': time.time()}
        block = chain.update_chain(block_data)
        chain.broadcast_block(list(block))

        self.finish({'folder':folder_name, 'block': list(block)})

        # except:
        #     pass


class RemoveFolderHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('chain test')

class AddFilesHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('chain test')

class RemoveFilesHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('chain test')

class AddDeviceHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('chain test')

class SetDeviceHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('chain test')

