
import sys
import os
import hashlib
import json
import time
import pprint
import urllib.parse

import requests

from chunk import MAX_CHUNK_SIZE
# from chunk import group0_quota

from chunk import mt_combine
# from chunk import chunks_to_partition
# update_folder.py url folder_name folder_meta_hash


if __name__ == '__main__':
    ip_and_port = sys.argv[1]
    print('ip_and_port', sys.argv[1])
    folder_name = sys.argv[2]
    print('folder_name', sys.argv[2])
    folder_meta_hash = sys.argv[3]
    print('folder_meta_hash', sys.argv[3])

    res = requests.post('http://%s/*update_folder' % ip_and_port, {'folder_name': folder_name, 'folder_meta_hash': folder_meta_hash})
    print('update_folder', res.text)
