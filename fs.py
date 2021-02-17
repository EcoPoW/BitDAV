
import os
import argparse
import uuid
import time
import hashlib
import copy

import tornado.web
import tornado.httpclient
import tornado.escape

import ecdsa

import database



class TestHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('chain test')


