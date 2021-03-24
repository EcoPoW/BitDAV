
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
                meta_hash = block_data.get('meta_hash', '')
                # update_time = block_data['update_time']
                # if name:
                folder_names[name] = meta_hash #[items, update_time]
    print('get_folders', folder_names)
    return folder_names

storage_names = {}
def get_storages(reload=False):
    global storage_names
    pirmary = None
    if storage_names or not reload:
        storage_names = {}
        for block in chain.get_chain():
            block_data_json = block[5]
            block_data = tornado.escape.json_decode(block_data_json)
            print('get_storages', block_data)
            # print(names)
            if block_data.get('type') == 'storage':
                # if 'name' in block_data:
                name = block_data['name']
                path = block_data.get('path', '')
                # update_time = block_data['update_time']
                # if name:
                storage_names[name] = path #[items, update_time]
    print('get_storages', storage_names)
    return storage_names


class TestHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('chain test')


class GetFolderHandler(tornado.web.RequestHandler):
    def get(self):
        folder_name = self.get_argument('folder_name')
        names = get_folders()
        folder_meta_hash = names.get(folder_name, '')
        self.finish({'name': folder_name, 'meta_hash': folder_meta_hash})


class AddFolderHandler(tornado.web.RequestHandler):
    def get(self):
        names = get_folders()
        self.finish('%s<br><form method="POST"><input name="folder_name"/><input type="submit" value="Add"/></form>' % names)

    @tornado.gen.coroutine
    def post(self):
        folder_name = self.get_argument('folder_name')

        # need to check if the name already exists in the chain
        block_data = {'type': 'folder', 'name': folder_name, 'meta_hash': '', 'timestamp': time.time()}
        block = chain.update_chain(block_data)
        chain.broadcast_block(list(block))

        self.finish({'folder':folder_name, 'block': list(block)})


class RemoveFolderHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('chain test')

    @tornado.gen.coroutine
    def post(self):
        folder_name = self.get_argument('folder_name')

class UpdateFolderHandler(tornado.web.RequestHandler):
    def get(self):
        folder_name = self.get_argument('folder_name')
        names = get_folders()
        assert folder_name in names
        folder_meta_hash = names.get(folder_name)

        self.finish('%s<br><form method="POST"><input name="folder_name"/><input name="folder_meta_hash"/><input type="submit" value="Update"/></form>' % names)

    @tornado.gen.coroutine
    def post(self):
        folder_name = self.get_argument('folder_name')
        folder_meta_hash = self.get_argument('folder_meta_hash')

        names = get_folders()
        assert folder_name in names
        # folder_meta_hash = names.get(folder_name)
        # assert folder_meta_hash
        # folder_meta_data = {'type':'folder_meta', 'name': folder_name, 'items':[]}
        # if folder_meta_hash:

        storages = get_storages()
        if not storages:
            self.finish('no storage config')
            return

        for storage_path in storages.values():
            with open('%s/meta/%s' % (storage_path, folder_meta_hash), 'rb') as f:
                folder_meta_json = f.read()
                folder_meta_data = tornado.escape.json_decode(folder_meta_json)
                assert folder_meta_data['type'] == 'folder_meta'

        block_data = {'type': 'folder', 'name': folder_name, 'meta_hash': folder_meta_hash, 'timestamp': time.time()}
        block = chain.update_chain(block_data)
        chain.broadcast_block(list(block))

        self.finish({})

# class RemoveFilesHandler(tornado.web.RequestHandler):
#     def get(self):
#         self.finish('chain test')


class GetMetaHandler(tornado.web.RequestHandler):
    def get(self):
        storages = get_storages()
        if not storages:
            self.finish('no storage config')
            return

        folder_meta_hash = self.get_argument('folder_meta_hash')
        for storage_path in storages.values():
            if os.path.exists('%s/meta/%s' % (storage_path, folder_meta_hash)):
                with open('%s/meta/%s' % (storage_path, folder_meta_hash), 'rb') as f:
                    folder_meta_json = f.read()
                    folder_meta_data = tornado.escape.json_decode(folder_meta_json)
                    assert folder_meta_data['type'] == 'folder_meta'
                    self.finish(folder_meta_json)
                break


class UpdateStorageHandler(tornado.web.RequestHandler):
    def get(self):
        storages = get_storages()
        self.finish('%s<br><form method="POST"><input name="storage_name"/><input name="storage_path"/><input type="submit" value="Update"/></form>' % storages)

    def post(self):
        storage_name = self.get_argument('storage_name')
        storage_path = self.get_argument('storage_path')

        block_data = {'type': 'storage', 'name': storage_name, 'path': storage_path, 'timestamp': time.time()}
        block = chain.update_chain(block_data)
        chain.broadcast_block(list(block))

        self.finish({'storage': storage_name, 'block': list(block)})
