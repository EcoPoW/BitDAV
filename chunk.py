
import sys
import os
import hashlib
import json
import time
import pprint

# put file folder / filename
# chunk.py / filename

# will generate a meta for folder and file chunks
max_chunk_size = 1024*1024*100

# group 0
# pc1 300M
# pc2 1500M
group0_quota = [1024*1024*300, 1024*1024*1600]
group0_device_no = len(group0_quota)
group0_current_device_index = 0
quota = group0_quota[group0_current_device_index]
# group 1
# pc3 200M
# pc4 300M


def mt_combine(hash_list, algorithm):
    l = len(hash_list)
    m = l % 2
    result = []
    for i in range(0, l - m, 2):
        result.append((hash_list[i], hash_list[i+1], algorithm((hash_list[i][2] + hash_list[i+1][2]).encode("utf8")).hexdigest()))
    result.extend(hash_list[l-m:])
    return result

folder_meta_data = {'type':'folder_meta', 'items':[]}

print(sys.argv)

foldername = sys.argv[1]
for filename in sys.argv[2:]:
    # filename = sys.argv[2]

    with open(filename, 'rb') as f:
        group0 = []
        chunks = []
        filesize = 0

        while True:
            data = f.read(max_chunk_size)
            if not data:
                break
            chunk_hash = hashlib.sha256(data).hexdigest()
            chunk_size = len(data)
            filesize += chunk_size
            # print(chunk_hash, chunk_size)
            chunks.append([chunk_hash, chunk_size, group0_device_no-len(group0_quota)])
            # write file
            if quota < len(data):
                group0_current_device_index += 1
                quota = group0_quota[group0_current_device_index]

            quota -= len(data)
            print(quota)


    hash_list = mt_combine([c[0] for c in chunks], hashlib.sha256)
    while len(hash_list) > 1:
        hash_list = mt_combine(hash_list, hashlib.sha256)
    merkle_root = hash_list[0][-1]
    pprint.pprint(hash_list)


    file_meta_data = [os.path.basename(filename), merkle_root, filesize, time.time(), chunks]
    folder_meta_data['items'].append(file_meta_data)
    # pprint.pprint(file_meta_data)
    # file_meta_json = json.dumps(file_meta_data).encode()
    # file_meta_hash = hashlib.sha256(file_meta_json).hexdigest()
    # print(file_meta_hash, len(file_meta_json))

folder_meta_json = json.dumps(folder_meta_data).encode()
folder_meta_hash = hashlib.sha256(folder_meta_json).hexdigest()
with open('pc1/meta/%s' % folder_meta_hash, 'wb') as f:
    f.write(folder_meta_json)
print(folder_meta_hash, len(folder_meta_hash))
