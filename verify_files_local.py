
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
# add_files.py folder_name file_name ...


def main():
    print('folder meta hashes', sys.argv[1:])
    # folder_name = sys.argv[1]
    # res = requests.get('http://127.0.0.1:8001/*get_folder?folder_name=%s' % urllib.parse.quote(folder_name))
    # print('get_folder', res.json())
    folder_meta_hashes = sys.argv[1:]

    # else:
    #     return

    verified_chunks = set()
    for folder_meta_hash in sys.argv[1:]:

        if folder_meta_hash:
            with open('meta/%s' % folder_meta_hash, 'rb') as f:
                folder_meta_json = f.read()
                folder_meta_data = json.loads(folder_meta_json)
                assert folder_meta_data['type'] == 'folder_meta'

            for file_meta_data in folder_meta_data['items'].values():
                # [merkle_root, file_size, time.time(), chunks]
                file_chunks = file_meta_data[3]
                for chunk_hash, chunk_size, group in file_chunks:
                    if chunk_hash in verified_chunks:
                        continue
                    with open("blob/%s/%s" % (chunk_hash[:3], chunk_hash[3:]), 'rb') as f:
                        # group0 = []
                        # file_size = 0
                        data = f.read(chunk_size)
                        verify_chunk_hash = hashlib.sha256(data).hexdigest()
                        print(verify_chunk_hash, chunk_size)
                        assert chunk_hash == verify_chunk_hash
                        verified_chunks.add(chunk_hash)

if __name__ == '__main__':
    main()
