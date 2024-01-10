import json
import base64
from enum import Enum

class Message:
    def __init__(self, message="", type='broadcast', config=False, dest=None, origin=None, datatype='text'):
        self.message = message
        self.datatype = datatype # can be file_chunk, text, config object
        self.type = type
        self.config = config
        self.origin = origin
        self.dest = dest
        self.username = None

    def get_config(self):
        return self.config

    def get_type(self):
        return self.type

    def get_message(self):
        return self.message
    
    def get_dest(self):
        return self.dest

    def get_origin(self):
        return self.origin
    
    def get_datatype(self):
        return self.datatype
    
    def set_datatype(self, datatype):
        self.datatype = datatype
    
    def set_type(self, type):
        self.type = type

    def set_origin(self, origin):
        self.origin = origin

    def set_username(self, username):
        self.username = username

    def set_message(self, message):
        self.message = message

    def set_config(self, config):
        self.config = config

    def set_dest(self, dest):
        self.dest = dest
    
    def json(self):
        message_content = self.__dict__
        return json.dumps(message_content)

    def load_json(self, json_object):
        # self.message = message
        # self.type = type
        # self.config = config
        # self.origin = origin
        # self.dest = dest
        # self.username = None
        setters = {
            'message': self.set_message,
            'type': self.set_type,
            'config': self.set_config,
            'origin': self.set_origin,
            'dest': self.set_dest,
            'username': self.set_username,
            'datatype': self.set_datatype
            }
        for key in json_object:
            setters[key](json_object[key])

    def __str__(self):
        # return self.json()
        if self.username:
            return f'[{self.type}] {self.username}: {self.message}'
        return f'[{self.type}] {self.message}'
    
# m = Message("hello world")
# j = m.json()
# r = Message()
# r.load_json(json.loads(j))

# print(r)