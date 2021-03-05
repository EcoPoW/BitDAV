
import sys
import os
import hashlib
import json
import time
import pprint

from chunk import MAX_CHUNK_SIZE
from chunk import chunks_to_partition


# group 0
# pc1 300M
# pc2 1500M
# group0_quota = [1024*1024*300+12, 1024*1024*1600]
group0_quota = [1000*1000*300+12, 1000*1000*1600]
group0_device_no = len(group0_quota)
group0_current_device_index = 0

new_group0_quota = [1024*1024*150, 1024*1024*1600]
new_group0_device_no = len(new_group0_quota)
quota = group0_quota[group0_current_device_index]
# group 1
# pc3 200M
# pc4 300M

if __name__ == '__main__':
    print(sys.argv[2:])
    folder_meta_hash = sys.argv[1]
    folder_meta_json = open('pc1/meta/%s' % folder_meta_hash, 'rb').read()
    folder_meta_data = json.loads(folder_meta_json)

    print('folder_meta_hash', folder_meta_hash, len(folder_meta_json))
    pprint.pprint(folder_meta_data)

    chunks_to_move = {}
    for file_meta_data in folder_meta_data['items']:
        # print(file_meta_data)
        chunks = file_meta_data[4]
        # print(chunks)
        for chunk in chunks:
            device = chunk[2]
            chunks_to_move.setdefault(device, set())
            chunks_to_move[device].add(tuple(chunk))
    print('chunks_to_move fill')
    pprint.pprint(chunks_to_move)

    new_group0_quota_left = []
    for device, quota in enumerate(new_group0_quota):
        chunks_to_move.setdefault(device, set())
        if device < group0_device_no:
            chunks_to_stay = set()
            for chunk in chunks_to_move[device]:
                # chunk_hash = chunk[0]
                chunk_size = chunk[1]
                if quota >= chunk_size:
                    quota -= chunk_size
                    # print(quota)
                    chunks_to_stay.add(chunk)
            chunks_to_move[device] -= chunks_to_stay
            # pprint.pprint(chunks_to_stay)
        new_group0_quota_left.append(quota)
    print('chunks_to_move stay')
    pprint.pprint(chunks_to_move)

    chunks_to_move, new_group0_quota_left = chunks_to_partition(chunks_to_move[0], new_group0_quota_left)
    print('chunks_to_move')
    pprint.pprint(chunks_to_move)

    # folder_meta_data_items = []
    for file_meta_data in folder_meta_data['items']:
        # print(file_meta_data)
        chunks = file_meta_data[4]
        # print(chunks)
        new_chunks = []
        for chunk_hash, chunk_size, device in chunks:
            chunk = tuple([chunk_hash, chunk_size, device])
            if chunk in chunks_to_move:
                new_chunks.append([chunk_hash, chunk_size, chunks_to_move[chunk]])
            else:
                new_chunks.append([chunk_hash, chunk_size, device])
        file_meta_data[4] = new_chunks
        # folder_meta_data_items.append(file_meta_data)
    # folder_meta_data['items'] = folder_meta_data_items
    pprint.pprint(folder_meta_data)
    folder_meta_json = json.dumps(folder_meta_data).encode()
    folder_meta_hash = hashlib.sha256(folder_meta_json).hexdigest()
    with open('pc1/meta/%s' % folder_meta_hash, 'wb') as f:
        f.write(folder_meta_json)
    print('new folder_meta_hash', folder_meta_hash, len(folder_meta_json))


    print('group0_quota         ', group0_quota)
    print('new_group0_quota     ', new_group0_quota)
    print('new_group0_quota_left', new_group0_quota_left)

