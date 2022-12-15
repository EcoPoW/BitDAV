
import sys
import os
import hashlib
import json
import time
import pprint

import requests

import chunk

if __name__ == '__main__':
    # print(sys.argv[2:])
    ip_and_port = sys.argv[1]
    print('ip_and_port', ip_and_port)
    rsp = requests.get('http://%s/*get_folders' % ip_and_port)
    folders = rsp.json()["folders"]
    chunks = set()
    for folder_name, folder_meta_hash in folders.items():
        print(folder_name, folder_meta_hash)
        rsp = requests.get('http://%s/*get_meta?folder_meta_hash=%s' % (ip_and_port, folder_meta_hash))
        folder_items = rsp.json()["items"]

        for file_name, file_item in folder_items.items():
            file_chunks = file_item[3]
            for file_chunk in file_chunks:
                chunk_hash = file_chunk[0]
                # print(chunk_hash)
                chunks.add(chunk_hash)

    print('total chunks', len(chunks))

    rsp = requests.get('http://%s/*get_storage' % ip_and_port)
    pprint.pprint(rsp.json())
    nodes = rsp.json()["nodes"]
    storages = rsp.json()["storages"]
    remote_storages = rsp.json()["remote_storages"]
    for storage_name, storage_info in storages.items():
        print(storage_name, storage_info)
        local_group = storage_info[2]
        # how many chunks I have local with local_group?
        for remote_storage_name, remote_storage_info in remote_storages.items():
            remote_node_name = remote_storage_info[1]
            remote_group = remote_storage_info[2]
            if local_group != remote_group:
                host, port = nodes[remote_node_name]
                print(remote_node_name, host, port, remote_group)
                for file_blob_hash in chunks:
                    rsp = requests.get('http://%s:%s/*get_blob?file_blob_hash=%s' % (host, port, file_blob_hash))
                    print(file_blob_hash, len(rsp.content))


    # for a given group
    # scan all remote storages
    # 

    # folder_meta_hash = sys.argv[1]
    # folder_meta_json = open('pc1/meta/%s' % folder_meta_hash, 'rb').read()
    # folder_meta_data = json.loads(folder_meta_json)

    # print('folder_meta_hash', folder_meta_hash, len(folder_meta_json))
    # pprint.pprint(folder_meta_data)

    # chunks_to_move = {}
    # for file_meta_data in folder_meta_data['items']:
    #     # print(file_meta_data)
    #     chunks = file_meta_data[4]
    #     # print(chunks)
    #     for chunk in chunks:
    #         device = chunk[2]
    #         chunks_to_move.setdefault(device, set())
    #         chunks_to_move[device].add(tuple(chunk))
    # print('chunks_to_move fill')
    # pprint.pprint(chunks_to_move)

    # new_group0_quota_left = []
    # for device, quota in enumerate(new_group0_quota):
    #     chunks_to_move.setdefault(device, set())
    #     if device < group0_device_no:
    #         chunks_to_stay = set()
    #         for chunk in chunks_to_move[device]:
    #             # chunk_hash = chunk[0]
    #             chunk_size = chunk[1]
    #             if quota >= chunk_size:
    #                 quota -= chunk_size
    #                 # print(quota)
    #                 chunks_to_stay.add(chunk)
    #         chunks_to_move[device] -= chunks_to_stay
    #         # pprint.pprint(chunks_to_stay)
    #     new_group0_quota_left.append(quota)
    # print('chunks_to_move stay')
    # pprint.pprint(chunks_to_move)

    # chunks_to_move, new_group0_quota_left = chunks_to_partition(chunks_to_move[0], new_group0_quota_left)
    # print('chunks_to_move')
    # pprint.pprint(chunks_to_move)

    # # folder_meta_data_items = []
    # for file_meta_data in folder_meta_data['items']:
    #     # print(file_meta_data)
    #     chunks = file_meta_data[4]
    #     # print(chunks)
    #     new_chunks = []
    #     for chunk_hash, chunk_size, device in chunks:
    #         chunk = tuple([chunk_hash, chunk_size, device])
    #         if chunk in chunks_to_move:
    #             new_chunks.append([chunk_hash, chunk_size, chunks_to_move[chunk]])
    #         else:
    #             new_chunks.append([chunk_hash, chunk_size, device])
    #     file_meta_data[4] = new_chunks
    #     # folder_meta_data_items.append(file_meta_data)
    # # folder_meta_data['items'] = folder_meta_data_items
    # pprint.pprint(folder_meta_data)
    # folder_meta_json = json.dumps(folder_meta_data).encode()
    # folder_meta_hash = hashlib.sha256(folder_meta_json).hexdigest()
    # with open('pc1/meta/%s' % folder_meta_hash, 'wb') as f:
    #     f.write(folder_meta_json)
    # print('new folder_meta_hash', folder_meta_hash, len(folder_meta_json))


    # print('group0_quota         ', group0_quota)
    # print('new_group0_quota     ', new_group0_quota)
    # print('new_group0_quota_left', new_group0_quota_left)

