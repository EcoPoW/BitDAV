
import sys
import os
import hashlib
import json
import time
import pprint

# put file folder / filename
# chunk.py / filename

# will generate a meta for folder and file chunks
MAX_CHUNK_SIZE = 1024*1024*10

# group 0
# pc1 300M
# pc2 1500M
group0_quota = [1024*1024*300, 1024*1024*1600]
group0_device_no = len(group0_quota)
group0_current_device_index = 0

new_group0_quota = [1024*1024*150, 1024*1024*1600]
new_group0_device_no = len(new_group0_quota)
quota = group0_quota[group0_current_device_index]
# group 1
# pc3 200M
# pc4 300M


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
pprint.pprint(chunks_to_move)

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
pprint.pprint(chunks_to_move)
     
