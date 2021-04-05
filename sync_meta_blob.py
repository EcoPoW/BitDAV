
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
    print(ip_and_port)

    # get_storage
    # will return current storage path and remote nodes IP and port
    res = requests.get('http://%s/*get_storage' % ip_and_port)
    # print(res.json())
    storages_path = []
    for storage_name, storage_path in res.json()['storages'].items():
        print(storage_name, storage_path)
        storages_path.append(storage_path)
    nodes = res.json()['nodes']

    # request get_folders
    res = requests.get('http://%s/*get_folders' % ip_and_port)
    # print(res.json())
    folders_meta_hash = []
    for folder_name, folder_meta_hash in res.json()['folders'].items():
        print(folder_name, folder_meta_hash)
        folders_meta_hash.append(folder_meta_hash)

    for storage_path in storages_path:
        for folder_meta_hash in folders_meta_hash:
            # print(storage_path)
            for host, port in nodes:
                print(folder_meta_hash)
                if not os.path.exists(os.path.join(storage_path, 'meta', folder_meta_hash)):
                    res = requests.get("http://%s:%s/*get_meta?folder_meta_hash=%s" % (host, port, folder_meta_hash))
                    assert folder_meta_hash == hashlib.sha256(res.text.encode('utf8')).hexdigest()
                    with open(os.path.join(storage_path, 'meta', folder_meta_hash), 'wb') as f:
                        f.write(res.text.encode('utf8'))
                        print('download')
                    break

    # get_meta
    # get_blob


if __name__ == '__main__':
    main()
