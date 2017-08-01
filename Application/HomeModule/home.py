import tornado.options
import tornado.web
from SettingsModule.settings import user_collection_name, jwt_secret
from LoggingModule.logging import logger
from tornado.ioloop import IOLoop
import hashlib
import jwt
import json 

#https://emptysqua.re/blog/refactoring-tornado-coroutines/
## finding user from motor  yields a future object which is nothing but a promise that it will have a value in future
## and gen.coroutine is a perfect to resolve a future object uyntillit is resolved

from generic.cors import cors


class Home(tornado.web.RequestHandler):
    
    def get(self):
        self.write("Hello, world")