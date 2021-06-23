
import os
import argparse
import uuid
import time
import hashlib
import copy
import shutil

import tornado.web
import tornado.httpclient
import tornado.escape

# import ecdsa

import database
import chain

from chunk import MAX_CHUNK_SIZE

folder_names = {}
def get_folders(reload=False):
    global folder_names
    pirmary = None
    if folder_names or not reload:
        folder_names = {}
        for block in chain.get_chain():
            block_data_json = block[5]
            block_data = tornado.escape.json_decode(block_data_json)
            # print(names)
            if block_data.get('type') == 'folder':
                print('get_folders block', block_data)
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
            # print(names)
            if block_data.get('type') == 'storage':
                print('get_storages block', block_data)
                # if 'name' in block_data:
                name = block_data['name']
                path = block_data.get('path', '')
                node_name = block_data.get('node_name', '')
                # if name:
                storage_names[name] = [path, node_name]
    print('get_storages', storage_names)
    return storage_names


class TestHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('chain test')


class ListFoldersHandler(tornado.web.RequestHandler):
    def get(self):
        names = get_folders()
        for folder_name, folder_meta_hash in names.items():
            self.write('<a href="/%s">%s<br>' % (folder_name, folder_name))
        self.finish()


class ListFilesHandler(tornado.web.RequestHandler):
    def get(self, folder_name):
        storages = get_storages()
        if not storages:
            self.finish('no storage config')
            return

        # folder_name = self.get_argument('folder_name')
        names = get_folders()
        folder_meta_hash = names.get(folder_name, '')
        # self.finish({'name': folder_name, 'meta_hash': folder_meta_hash})

        # folder_meta_hash = self.get_argument('folder_meta_hash')
        self.write('<a href="/*update_folder?folder_name=%s">Add</a>' % (folder_name))
        self.write('<h1>%s</h1>' % (folder_name))

        for storage_name, storage_payload in storages.items():
            storage_path = storage_payload[0]
            node_name = storage_payload[1]
            if node_name == chain.current_name:
                folder_meta_path = os.path.join(storage_path, 'meta', folder_meta_hash)
                if os.path.exists(folder_meta_path):
                    with open(folder_meta_path, 'rb') as f:
                        folder_meta_json = f.read()
                        folder_meta_data = tornado.escape.json_decode(folder_meta_json)
                        assert folder_meta_data['type'] == 'folder_meta'
                        for file_name in folder_meta_data.get('items', {}):
                            self.write('<a href="/%s/%s">%s</a><br>' % (folder_name, file_name, file_name))
                        break


class GetFileHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self, folder_name, file_name):
        # self.finish("%s %s" %(folder_name, file_name))
        folders = get_folders()
        folder_meta_hash = folders.get(folder_name, '')
        storages = get_storages()

        # find a local storage (set)
        for storage_name, storage_payload  in storages.items():
            storage_path = storage_payload[0]
            node_name = storage_payload[1]
            if node_name == chain.current_name:
                # self.write(storage_name)
                # self.write(tornado.escape.json_encode(storage_payload))

                # look up folder_meta_hash content
                folder_meta_path = os.path.join(storage_path, 'meta', folder_meta_hash)
                if os.path.exists(folder_meta_path):
                    with open(folder_meta_path, 'rb') as f:
                        folder_meta_json = f.read()
                        folder_meta_data = tornado.escape.json_decode(folder_meta_json)
                        assert folder_meta_data['type'] == 'folder_meta'
                        # self.write('%s %s<br> %s<br>' % (folder_name, file_name, folder_meta_data.get('items', {})))
                        if file_name in folder_meta_data.get('items', {}):
                            item = folder_meta_data.get('items', {})[file_name]
                            chunks = item[3]
                            # break
                # else:
                #     self.finish('not found')
                #     return

                self.set_header('Content-Type', 'application/octet-stream')
                for chunk in chunks:
                    file_blob_hash = chunk[0]
                    file_blob_path = os.path.join(storage_path, 'blob', file_blob_hash[:3], file_blob_hash)
                    with open(file_blob_path, 'rb') as f:
                        self.write(f.read())
                break

        # check file_name and get storage
        # get storage IP and port if not local
        # fetch and respone if not 404
        # http_client = tornado.httpclient.AsyncHTTPClient()

        # names, pirmary = chain.get_names()
        # for name, info in names.items():
        #     host, port, pk = info
        #     self.finish('%s %s' % (folder_name, file_name))


# @tornado.web.stream_request_body
class UploadFileHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('''<br><form method="POST" enctype="multipart/form-data">
            <input name="folder_name" placeholder="Folder" />
            <input name="dir_name" placeholder="Dir" />
            <input name="file" type="file" />
            <input type="submit" value="Upload"/></form>''')

    def post(self):
        storages = get_storages()
        if not storages:
            self.finish('no storage config')
            return
        
        for storage_name, storage_payload in storages.items():
            node_name = storage_payload[1]
            if node_name == chain.current_name:
                storage_path = storage_payload[0]
                if shutil.disk_usage(storage_path).free > 2**20*128:
                    break

        for name, files in self.request.files.items():
            print('===')
            for file in files:
                filename = file["filename"]
                content_type = file["content_type"]
                body = file["body"]
                print(filename, content_type, len(body), type(body))

                i = 0
                j = 0
                for j in range(MAX_CHUNK_SIZE, len(body), MAX_CHUNK_SIZE):
                    print(i, j)
                    print(hashlib.sha256(body[i:j]).hexdigest())
                    i = j
                else:
                    print(j, len(body))
                    print(hashlib.sha256(body[j:len(body)]).hexdigest())


    # def initialize(self):
    #     self.bytes_read = 0

    # def data_received(self, chunk):
    #     self.bytes_read += len(chunk)
    #     print('POST', self.bytes_read)
    #     print('POST', chunk)

    # def post(self):
    #     print('===')
    #     mtype = self.request.headers.get("Content-Type")
    #     print('POST', mtype, self.bytes_read)
    #     self.write("OK")

class GetFoldersHandler(tornado.web.RequestHandler):
    def get(self):
        folders = get_folders()
        result = {"folders": {}}
        for folder_name, folder_meta_hash in folders.items():
            # folder_meta_hash = folders.get(folder_name, '')
            if folder_name and folder_meta_hash:
                result["folders"][folder_name] = folder_meta_hash
        self.finish(result)


class GetFolderHandler(tornado.web.RequestHandler):
    def get(self):
        folder_name = self.get_argument('folder_name')
        folders = get_folders()
        folder_meta_hash = folders.get(folder_name, '')
        self.finish({'name': folder_name, 'meta_hash': folder_meta_hash})


class AddFolderHandler(tornado.web.RequestHandler):
    def get(self):
        names = get_folders()
        self.finish('''%s<br><form method="POST">
            <input name="folder_name" placeholder="Folder" />
            <input type="submit" value="Add"/></form>\n''' % names)

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

        self.finish('''%s<br><form method="POST">
            <input name="folder_name" placeholder="Folder" />
            <input name="folder_meta_hash" placeholder="Meta Hash" />
            <input type="submit" value="Update"/></form>''' % names)

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

        for storage_payload in storages.values():
            storage_path = storage_payload[0]
            node_name = storage_payload[1]
            folder_meta_path = os.path.join(storage_path, 'meta', folder_meta_hash)
            if os.path.exists(folder_meta_path):
                with open(folder_meta_path, 'rb') as f:
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
        for storage_path, _ in storages.values():
            folder_meta_path = os.path.join(storage_path, 'meta', folder_meta_hash)
            if os.path.exists(folder_meta_path):
                with open(folder_meta_path, 'rb') as f:
                    folder_meta_json = f.read()
                    folder_meta_data = tornado.escape.json_decode(folder_meta_json)
                    assert folder_meta_data['type'] == 'folder_meta'
                    self.finish(folder_meta_json)
                break


class UpdateMetaHandler(tornado.web.RequestHandler):
    def post(self):
        storages = get_storages()
        if not storages:
            self.finish('no storage config')
            return

class GetBlobHandler(tornado.web.RequestHandler):
    def get(self):
        storages = get_storages()
        if not storages:
            self.finish('no storage config')
            return


class UpdateBlobHandler(tornado.web.RequestHandler):
    def post(self):
        storages = get_storages()
        if not storages:
            self.finish('no storage config')
            return


class UpdateStorageHandler(tornado.web.RequestHandler):
    def get(self):
        storages = get_storages()
        self.write('''%s<br><form method="POST">
            <input name="storage_name" placeholder="Storage Name" />
            <input name="storage_path" placeholder="Storage Path" />
            <input name="group" placeholder="Group 0 or 1" />
            <input type="submit" value="Update" /></form>''' % storages)

    def post(self):
        storage_name = self.get_argument('storage_name')
        storage_path = self.get_argument('storage_path')
        node_name = self.get_argument('node_name', chain.current_name)
        group = self.get_argument('group')
        # print('storage_path', storage_path)

        block_data = {'type': 'storage', 'name': storage_name, 'path': storage_path, 'node_name': node_name, 'group': group, 'timestamp': time.time()}
        block = chain.update_chain(block_data)
        chain.broadcast_block(list(block))

        self.finish({'storage': storage_name, 'block': list(block)})

class GetStorageHandler(tornado.web.RequestHandler):
    def get(self):
        result = {'storages':{}, 'node_name': chain.current_name, 'nodes':{}}
        storages = get_storages()
        for storage_name, storage_payload in storages.items():
            storage_path = storage_payload[0]
            node_name = storage_payload[1]
            try:
                group = storage_payload[2]
            except:
                group = '0'
            if node_name == chain.current_name:
                disk = shutil.disk_usage(storage_path)
                result['storages'][storage_name] = [storage_path, node_name, group, disk.free]

        names, pirmary = chain.get_names()
        for name, info in names.items():
            host, port, pk = info
            # if name != chain.current_name:
            result['nodes'][name] = [host, port]

        self.finish(result)
