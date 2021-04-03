
import sys
import os
import hashlib
import json
import time
import pprint
import urllib.parse

# import requests

from chunk import MAX_CHUNK_SIZE
from chunk import group0_quota

from chunk import mt_combine
from chunk import chunks_to_partition
# get_files_local_with_meta.py folder_meta_file


if __name__ == '__main__':
    print('meta', sys.argv[1])
    folder_meta_file = sys.argv[1]

    with open(folder_meta_file, 'rb') as f:
        folder_meta_json = f.read()
        folder_meta_data = json.loads(folder_meta_json)
        assert folder_meta_data['type'] == 'folder_meta'

    for item in folder_meta_data['items']:
        print(item[0])
        for chunk in item[4]:
            print('  |- ', chunk[0])


    # for folder_name in sys.argv[2:]:
    #     files = os.scandir(folder_name)

    #     for f in files:
    #         file_name = folder_name+f.name
    #         file_chunks = []
    #         with open(file_name, 'rb') as f:
    #             # group0 = []
    #             file_size = 0

    #             while True:
    #                 data = f.read(MAX_CHUNK_SIZE)
    #                 if not data:
    #                     break
    #                 chunk_hash = hashlib.sha256(data).hexdigest()
    #                 chunk_size = len(data)
    #                 file_size += chunk_size
    #                 print(chunk_hash, chunk_size)
    #                 # chunks.append([chunk_hash, chunk_size, group0_device_no-len(group0_quota)])
    #                 file_chunks.append((chunk_hash, chunk_size))
    #                 # write file
    #                 with open('pc1/blob/%s' % chunk_hash, 'wb') as fw:
    #                     fw.write(data)
    #                 # if quota < chunk_size:
    #                 #     group0_current_device_index += 1
    #                 #     quota = group0_quota[group0_current_device_index]

    #                 # quota -= chunk_size
    #                 # print('quota', group0_current_device_index, quota)

    #         chunks_to_go, group0_quota_left = chunks_to_partition(file_chunks, group0_quota)
    #         pprint.pprint(chunks_to_go)
    #         chunks = []
    #         for chunk_hash, chunk_size in file_chunks:
    #             chunks.append([chunk_hash, chunk_size, chunks_to_go[(chunk_hash, chunk_size)]])

    #         print('chunks', chunks, len(chunks))
    #         hash_list = mt_combine([c[0:1] for c in chunks], hashlib.sha256)
    #         while len(hash_list) > 1:
    #             pprint.pprint(hash_list)
    #             print('---')
    #             hash_list = mt_combine(hash_list, hashlib.sha256)
    #         merkle_root = hash_list[0][-1]

    #         file_meta_data = [os.path.basename(file_name), merkle_root, file_size, time.time(), chunks]
    #         folder_meta_data['items'].append(file_meta_data)

    #     folder_meta_json = json.dumps(folder_meta_data).encode()
    #     folder_meta_hash = hashlib.sha256(folder_meta_json).hexdigest()
    #     with open('pc1/meta/%s' % folder_meta_hash, 'wb') as f:
    #         f.write(folder_meta_json)
    #     print('folder_meta_hash', folder_meta_hash, len(folder_meta_json))

