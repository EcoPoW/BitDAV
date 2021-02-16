
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
group0_quota = [1024*1024*100, 1024*1024*1600]
# group0_device_no = len(group0_quota)
# group0_current_device_index = 0
# quota = group0_quota[group0_current_device_index]
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

def chunks_to_partition(chunks, partition_free_sizes):
    # chunks: [(chunk_hash, chunk_size), ...]
    # partition_free_sizes: [free_size, ...]
    result = {}
    left_free_sizes = []
    index = 0
    free_size = partition_free_sizes[index]
    for chunk in chunks:
        chunk_hash = chunk[0]
        chunk_size = chunk[1]
        if free_size < chunk_size:
            left_free_sizes.append(free_size)
            index += 1
            free_size = partition_free_sizes[index]
        free_size -= chunk_size
        result[chunk] = index
    left_free_sizes.append(free_size)
    return result, left_free_sizes

if __name__ == '__main__':
    print(sys.argv[2:])
    foldername = sys.argv[1]
    folder_meta_data = {'type':'folder_meta', 'name': foldername, 'items':[]}
    for filename in sys.argv[2:]:
        file_chunks = []
        with open(filename, 'rb') as f:
            # group0 = []
            filesize = 0

            while True:
                data = f.read(MAX_CHUNK_SIZE)
                if not data:
                    break
                chunk_hash = hashlib.sha256(data).hexdigest()
                chunk_size = len(data)
                filesize += chunk_size
                # print(chunk_hash, chunk_size)
                # chunks.append([chunk_hash, chunk_size, group0_device_no-len(group0_quota)])
                file_chunks.append([chunk_hash, chunk_size])
                # write file
                # if quota < chunk_size:
                #     group0_current_device_index += 1
                #     quota = group0_quota[group0_current_device_index]

                # quota -= chunk_size
                # print('quota', group0_current_device_index, quota)

        chunks_to_go, group0_quota_left = chunks_to_partition(file_chunks, group0_quota)
        pprint.pprint(chunks_to_go)
        chunks = []
        for chunk_hash, chunk_size in file_chunks:
            chunks.append([chunk_hash, chunk_size, chunks_to_go[(chunk_hash, chunk_size)]])

        print('chunks', chunks, len(chunks))
        hash_list = mt_combine([c[0:1] for c in chunks], hashlib.sha256)
        while len(hash_list) > 1:
            pprint.pprint(hash_list)
            print('---')
            hash_list = mt_combine(hash_list, hashlib.sha256)
        merkle_root = hash_list[0][-1]


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
    print('folder_meta_hash', folder_meta_hash, len(folder_meta_json))
