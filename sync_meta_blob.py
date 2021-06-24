
import sys
import os
import hashlib
import json
import time
import pprint
import urllib.parse

import requests


# sync_meta_blob.py IP:PORT


def main():
    # print('files', sys.argv[3:])
    # folder_name = sys.argv[2]
    ip_and_port = sys.argv[1]
    print('ip_and_port', ip_and_port)

    # get_storage
    # will return current storage path and remote nodes IP and port
    res = requests.get('http://%s/*get_storage' % ip_and_port)
    # print(res.json())
    storages_path = []
    storage_data = res.json()
    for storage_name, storage_payload in storage_data['storages'].items():
        print(storage_name, storage_payload)
        node_name = storage_payload[1]
        if storage_data['node_name'] == node_name:
            storage_path = storage_payload[0]
            storages_path.append(storage_path)

            os.makedirs(os.path.join(storage_path, 'meta'), exist_ok=True)
            for i in '0123456789abcdef':
                for j in '0123456789abcdef':
                    for k in '0123456789abcdef':
                        os.makedirs(os.path.join(storage_path, 'blob', i+k+j), exist_ok=True)

    nodes = storage_data['nodes']

    # request get_folders
    res = requests.get('http://%s/*get_folders' % ip_and_port)
    # print(res.json())
    folders_meta_hash = []
    for folder_name, folder_meta_hash in res.json()['folders'].items():
        print(folder_name, folder_meta_hash)
        folders_meta_hash.append(folder_meta_hash)

    # get_meta
    for node_name, host_and_port in nodes.items():
        host = host_and_port[0]
        port = host_and_port[1]
        if node_name != storage_data['node_name']:
            print(host_and_port)
            for storage_path in storages_path:
                for folder_meta_hash in folders_meta_hash:
                    print(folder_meta_hash)
                    if not os.path.exists(os.path.join(storage_path, 'meta', folder_meta_hash)):
                        res = requests.get("http://%s:%s/*get_meta?folder_meta_hash=%s" % (host, port, folder_meta_hash))
                        if res.status_code != 200:
                            continue

                        assert folder_meta_hash == hashlib.sha256(res.text.encode('utf8')).hexdigest()
                        with open(os.path.join(storage_path, 'meta', folder_meta_hash), 'wb') as f:
                            f.write(res.text.encode('utf8'))
                            print('download')
                        break

    # get_blob


if __name__ == '__main__':
    main()
