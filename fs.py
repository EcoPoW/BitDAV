
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



class AddFolderHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('chain test')

class RemoveFolderHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('chain test')

class AddFilesHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('chain test')

class RemoveFilesHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('chain test')

class AddDeviceHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('chain test')

class SetDeviceHandler(tornado.web.RequestHandler):
    def get(self):
        self.finish('chain test')

