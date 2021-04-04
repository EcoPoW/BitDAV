
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
    # sync_meta_blob.py IP:PORT
    requests.get('http://%s/*get_storage', ip_and_port)

    # request get_folders

    # get_storage
    # will return current storage path and remote nodes IP and port

    # get_meta
    # get_blob


if __name__ == '__main__':
    main()
