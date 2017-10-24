import tornado.options
import tornado.web
from tornado.escape import json_decode as TornadoJsonDecode
from SettingsModule.settings  import domain_collection_name, indian_time, jwt_secret,\
									default_document_limit, user_collection_name, permission_collection_name,\
									 action_collection_name, concept_collection_name, subconcept_collection_name,\
									 nanoskill_collection_name, question_collection_name, image_collection_name,\
                                     bucket_name, access_key_id, secret_access_key, s3connection

##chan
from LoggingModule.logging import logger
import time 
import hashlib
from pprint import pprint
import jwt
import json
from AuthenticationModule.authentication import auth
import boto3
#from boto.s3.key import Key
from io import StringIO, BytesIO

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
        self.parent_collection = self.db[nanoskill_collection_name]


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
    def delete(self):
        parent_name = self.request.arguments.get("parent_name")[0].decode("utf-8")
        module_id = self.request.arguments.get("module_id")[0].decode("utf-8")
        image_name = self.request.arguments.get("image_name")[0].decode("utf-8")

        __name = "Questions/%s/%s/%s"%(parent_name, module_id, image_name)
        name = __name.lower().replace(" ", "").replace("nanoskill-", "")

        s3connection.delete_object(Bucket=bucket_name, Key=name)
        self.write({"message": "Image with name %s has been deleted"%image_name})
        self.finish()
        return


    
    @cors
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):

        pprint (self.request.arguments)
        user_id = self.request.arguments.get("user_id")[0].decode("utf-8")
        parent_id = self.request.arguments.get("parent_id")[0].decode("utf-8")
        module_id = self.request.arguments.get("module_id")[0].decode("utf-8")
        

        user = yield self.users.find_one({"user_id": user_id}, projection={"_id": False, "ngrams": False})
        parent = yield self.parent_collection.find_one({"module_id": parent_id}, projection={"_id": False, "ngrams": False})


        if not user or not parent:
            raise Exception("user_id and parent_id must be provided")

        arg = self.request.files["image_data"][0]

        image_data = self.request.files["image_data"][0].get("body")
        image_name = self.request.files["image_data"][0].get("filename")
        image_content_type = self.request.files["image_data"][0].get("content_type")

        image_id = hashlib.md5(image_name.encode("utf-8")).hexdigest()

        print(image_id)
        bytesIO = BytesIO()
        bytesIO.write(image_data)
        bytesIO.seek(0)
        
        __name = "Questions/%s/%s/%s"%(parent["module_name"], module_id, image_name)
        name = __name.lower().replace(" ", "").replace("nanoskill-", "")

        print (name)
        s3connection.put_object(Body=bytesIO, Bucket=bucket_name, Key=name, ContentType=image_content_type, Metadata= {"user_id": user_id, "nanoskill_id": parent_id, 
                                                                                                             "nanoskill_name": parent["module_name"], 
                                                                                                             "module_id": module_id }, Expires = 604800)

        __data = {"key": name , "user_name": user["username"], "user_id": user_id, "name": image_name}
        url = s3connection.generate_presigned_url('get_object', Params = {'Bucket': bucket_name, 'Key': name})
        yield self.questions.update_one({"module_id": module_id}, {"$set": {"images.%s"%str(image_id): __data}}, upsert=False)
        
        print (url)
        ##TODO: https://gist.github.com/kn9ts/4b5a9942b6afbfc2534f2f14c87b9b54
        ##TODO: https://github.com/jmenga/requests-aws-sign
        self.write({"link": url})
        self.finish()
        return


