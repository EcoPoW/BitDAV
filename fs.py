
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
        block_data = {'type': 'folder', 'name': folder_name, 'meta_hash': '', 'timestamp': time.time()}
        block = chain.update_chain(block_data)
        chain.broadcast_block(list(block))

        self.finish({'folder':folder_name, 'block': list(block)})

        # except:
        #     pass


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
        with open('pc1/meta/%s' % folder_meta_hash, 'rb') as f:
            folder_meta_json = f.read()
            folder_meta_data = tornado.escape.json_decode(folder_meta_json)
            assert folder_meta_data['type'] == 'folder_meta'

        # with open(file_name, 'rb') as f:
        #     # group0 = []
        #     filesize = 0

        #     while True:
        #         data = f.read(MAX_CHUNK_SIZE)
        #         if not data:
        #             break
        #         chunk_hash = hashlib.sha256(data).hexdigest()
        #         chunk_size = len(data)
        #         filesize += chunk_size
        #         # print(chunk_hash, chunk_size)
        #         # chunks.append([chunk_hash, chunk_size, group0_device_no-len(group0_quota)])
        #         file_chunks.append([chunk_hash, chunk_size])
        #         # write file
        #         # if quota < chunk_size:
        #         #     group0_current_device_index += 1
        #         #     quota = group0_quota[group0_current_device_index]

        #         # quota -= chunk_size
        #         # print('quota', group0_current_device_index, quota)

        # chunks_to_go, group0_quota_left = chunks_to_partition(file_chunks, group0_quota)
        # pprint.pprint(chunks_to_go)
        # chunks = []
        # for chunk_hash, chunk_size in file_chunks:
        #     chunks.append([chunk_hash, chunk_size, chunks_to_go[(chunk_hash, chunk_size)]])

        # print('chunks', chunks, len(chunks))
        # hash_list = mt_combine([c[0:1] for c in chunks], hashlib.sha256)
        # while len(hash_list) > 1:
        #     pprint.pprint(hash_list)
        #     print('---')
        #     hash_list = mt_combine(hash_list, hashlib.sha256)
        # merkle_root = hash_list[0][-1]


        # file_meta_data = [os.path.basename(filename), merkle_root, filesize, time.time(), chunks]
        # folder_meta_data['items'].append(file_meta_data)
        # # pprint.pprint(file_meta_data)
        # # file_meta_json = json.dumps(file_meta_data).encode()
        # # file_meta_hash = hashlib.sha256(file_meta_json).hexdigest()
        # # print(file_meta_hash, len(file_meta_json))

        # folder_meta_json = json.dumps(folder_meta_data).encode()
        # folder_meta_hash = hashlib.sha256(folder_meta_json).hexdigest()
        # with open('pc1/meta/%s' % folder_meta_hash, 'wb') as f:
        #     f.write(folder_meta_json)
        # print('folder_meta_hash', folder_meta_hash, len(folder_meta_json))

        block_data = {'type': 'folder', 'name': folder_name, 'meta_hash': folder_meta_hash, 'timestamp': time.time()}
        block = chain.update_chain(block_data)
        chain.broadcast_block(list(block))

        self.finish({})

# class RemoveFilesHandler(tornado.web.RequestHandler):
#     def get(self):
#         self.finish('chain test')


class GetMetaHandler(tornado.web.RequestHandler):
    def get(self):
        folder_meta_hash = self.get_argument('folder_meta_hash')
        with open('pc1/meta/%s' % folder_meta_hash, 'rb') as f:
            folder_meta_json = f.read()
            folder_meta_data = tornado.escape.json_decode(folder_meta_json)
            assert folder_meta_data['type'] == 'folder_meta'
            self.finish(folder_meta_json)


class AddDeviceHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('chain test')

class SetDeviceHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('chain test')

