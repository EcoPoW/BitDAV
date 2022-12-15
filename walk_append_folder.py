
import sys
import os
import hashlib
import json
import time
import pprint
import urllib.parse

import requests

from chunk import MAX_CHUNK_SIZE
from chunk import group0_quota

from chunk import mt_combine
from chunk import chunks_to_partition
# walk_append_folder.py folder_name folder_path [storage_path]

items_rename_counter = {}


if __name__ == '__main__':
    ip_and_port = sys.argv[1]
    print('ip_and_port', ip_and_port)

    folder_name = sys.argv[2]
    print('folder_name', folder_name)

    folder_path = sys.argv[3]
    print('folder_path', folder_path)

    # try:
    #     storage_path = sys.argv[3]
    # except:
    #     storage_path = './'
    # print('storage_path', storage_path)

    res = requests.get('http://%s/*get_storage' % ip_and_port)
    print('get_storage', res.json())
    node_name = res.json()['node_name']
    for storage_name, storage_payload in res.json()['storages'].items():
        storage_node_name = storage_payload[1]
        if storage_node_name == node_name:
            storage_path = storage_payload[0]
            break

    res = requests.get('http://%s/*get_folder?folder_name=%s' % (ip_and_port, urllib.parse.quote(folder_name)))
    print('get_folder', res.json())
    folder_meta_hash = res.json()['meta_hash']

    folder_meta_data = {'type':'folder_meta', 'name': folder_name, 'items':{}}
    if folder_meta_hash:
        res = requests.get('http://%s/*get_meta?folder_meta_hash=%s' % (ip_and_port, folder_meta_hash))
        if res.status_code == 200:
            folder_meta_json = res.text
            folder_meta_data = json.loads(folder_meta_json)

    for root, dirs, files in os.walk(folder_path):
        for fname in files:
            print(root, fname)
            file_name = os.path.join(root, fname)
            file_chunks = []
            # if f.is_dir():
            #     continue
            # print(fname)
            # continue

            with open(file_name, 'rb') as f:
                # group0 = []
                file_size = 0

                while True:
                    data = f.read(MAX_CHUNK_SIZE)
                    if not data:
                        break
                    chunk_hash = hashlib.sha256(data).hexdigest()
                    chunk_size = len(data)
                    file_size += chunk_size
                    print(chunk_hash, chunk_size)
                    file_chunks.append((chunk_hash, chunk_size))
                    # /*update_blob
                    while True:
                        try:
                            res = requests.post('http://%s/*update_blob?file_blob_hash=%s' % (ip_and_port, chunk_hash), data=data)
                            break
                        except requests.exceptions.ConnectionError:
                            print('retry %s' % chunk_hash)
                            time.sleep(1)
                    # write file 
                    # blob_path = os.path.join(storage_path, 'blob', chunk_hash[:3], chunk_hash)
                    # with open(blob_path, 'wb') as fw:
                    #     fw.write(data)

            chunks = []
            for chunk_hash, chunk_size in file_chunks:
                chunks.append([chunk_hash, chunk_size, []])

            print('chunks', chunks, len(chunks))
            hash_list = mt_combine([c[0:1] for c in chunks], hashlib.sha256)
            while len(hash_list) > 1:
                pprint.pprint(hash_list)
                print('---')
                hash_list = mt_combine(hash_list, hashlib.sha256)
            merkle_root = hash_list[0][-1]

            while True:
                name, ext = os.path.splitext(f.name)
                relative_path = (os.path.relpath(root, folder_path).replace('\\', '/')+'/').lstrip('./')
                unique_name = "%s%s%s%s" % (relative_path, os.path.basename(name), items_rename_counter.get(name, ''), ext)
                if unique_name not in folder_meta_data['items']:
                    break
                items_rename_counter.setdefault(name, 1)
                items_rename_counter[name] += 1

            file_meta_data = [merkle_root, file_size, time.time(), chunks]
            assert unique_name not in folder_meta_data['items']
            folder_meta_data['items'][unique_name] = file_meta_data
            # pprint.pprint(file_meta_data)
            # file_meta_json = json.dumps(file_meta_data).encode()
            # file_meta_hash = hashlib.sha256(file_meta_json).hexdigest()
            # print(file_meta_hash, len(file_meta_json))

    folder_meta_json = json.dumps(folder_meta_data).encode()
    folder_meta_hash = hashlib.sha256(folder_meta_json).hexdigest()
    # /*update_meta
    res = requests.post('http://%s/*update_meta?folder_meta_hash=%s' % (ip_and_port, folder_meta_hash), data=folder_meta_json)
    # with open(os.path.join(storage_path, 'meta', folder_meta_hash), 'wb') as f:
    #     f.write(folder_meta_json)
    print('folder_meta_hash', folder_meta_hash, len(folder_meta_json))

    res = requests.post('http://%s/*update_folder' % ip_and_port, {'folder_name': folder_name, 'folder_meta_hash': folder_meta_hash})
    print('update_folder', res.text)
