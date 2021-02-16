
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

new_group0_quota = [1024*1024*3, 1024*1024*1600]
new_group0_device_no = len(new_group0_quota)
quota = group0_quota[group0_current_device_index]
# group 1
# pc3 200M
# pc4 300M


def mt_combine(hash_list, algorithm):
    l = len(hash_list)
    m = l % 2
    result = []
    for i in range(0, l - m, 2):
        # print(hash_list[i][0], hash_list[i+1][0])
        result.append((hash_list[i][-1], hash_list[i+1][-1], algorithm((hash_list[i][-1] + hash_list[i+1][-1]).encode("utf8")).hexdigest()))
    result.extend(hash_list[l-m:])
    return result


print(sys.argv[2:])
folder_meta_hash = sys.argv[1]
folder_meta_json = open('pc1/meta/%s' % folder_meta_hash, 'rb').read()
folder_meta_data = json.loads(folder_meta_json)

print('folder_meta_hash', folder_meta_hash, len(folder_meta_json))
pprint.pprint(folder_meta_data)

for index in new_group0_device_no:
    pass

# for filename in sys.argv[2:]:
#     with open(filename, 'rb') as f:
#         group0 = []
#         chunks = []
#         filesize = 0

#         while True:
#             data = f.read(MAX_CHUNK_SIZE)
#             if not data:
#                 break
#             chunk_hash = hashlib.sha256(data).hexdigest()
#             chunk_size = len(data)
#             filesize += chunk_size
#             # print(chunk_hash, chunk_size)
#             chunks.append([chunk_hash, chunk_size, group0_device_no-len(group0_quota)])
#             # write file
#             if quota < len(data):
#                 group0_current_device_index += 1
#                 quota = group0_quota[group0_current_device_index]

#             quota -= len(data)
#             print('quota', group0_current_device_index,quota)


#     print('chunks', chunks, len(chunks))
#     hash_list = mt_combine([c[0:1] for c in chunks], hashlib.sha256)
#     while len(hash_list) > 1:
#         pprint.pprint(hash_list)
#         print('---')
#         hash_list = mt_combine(hash_list, hashlib.sha256)
#     merkle_root = hash_list[0][-1]
#     # pprint.pprint(hash_list)


#     file_meta_data = [os.path.basename(filename), merkle_root, filesize, time.time(), chunks]
#     folder_meta_data['items'].append(file_meta_data)
