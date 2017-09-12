import tornado.options
import tornado.web
from tornado.escape import json_decode as TornadoJsonDecode
from SettingsModule.settings  import domain_collection_name, indian_time, jwt_secret,\
									default_document_limit, user_collection_name, permission_collection_name,\
									 action_collection_name, concept_collection_name, subconcept_collection_name,\
									 nanoskill_collection_name, question_collection_name, image_collection_name
from LoggingModule.logging import logger
import time 
import hashlib
from pprint import pprint
import jwt
import json
from AuthenticationModule.authentication import auth
#https://emptysqua.re/blog/refactoring-tornado-coroutines/

import codecs
import math
from GeneralModule.cors import cors
reader = codecs.getreader("utf-8")

class UploadImage(tornado.web.RequestHandler):
    def initialize(self):
        self.db = self.settings["db"]
        self.images = self.db[image_collection_name]
        self.users = self.db[user_collection_name]
        self.questions = self.db[question_collection_name]


    @cors
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def options(self):
        self.set_status(204)
        self.finish()
        return 
        
        
    @cors
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):

        print (self.request.files)
        arg = json.loads(self.request.body)
        user_id = arg.get("user_id")
        project_id = arg.get("module_id")


        print (user_id)
        print (module_id)
        image_data = self.request.files["image_data"][0].get("body")
        image_name = self.request.files["image_data"][0].get("filename")

        #print (image_data)
        self.write({})
        self.finish()
        return


