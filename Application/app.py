#!/usr/bin/env python3
import tornado.httpserver
from tornado.ioloop import IOLoop
import signal
import tornado.options
import tornado.web
import tornado.httpclient
import motor
import urllib
import json
import datetime
import time
import uvloop
#from tornado.platform.asyncio import AsyncIOMainLoop
import asyncio
from tornaduv import UVLoop
#IOLoop.configure(UVLoop)
from SettingsModule.settings import app_port
from LoggingModule.logging import logger
from tornado.options import define, options
define("port", default=app_port, help="run on the given port", type=int)

#http://steelkiwi.com/blog/jwt-authorization-python-part-1-practise/
from LoginModule.login import Login
from SignupModule.signup import Signup
from SettingsModule.settings import mongo_db, nanoskill_collection_name, domain_collection_name,user_collection_name,\
                                            question_collection_name, concept_collection_name, subconcept_collection_name
from Ontology.DomainModule.domain import Domains
from Ontology.DomainModule.domain import DomainPermissions
from Ontology.ConceptModule.concept import Concepts, ConceptPermissions
from Ontology.NanoskillModule.nanoskill import Nanoskills, NanoskillPermissions


from Ontology.SubconceptModule.subconcept import Subconcepts, SubconceptPermissions
from Ontology.QuestionModule.question import Questions, QuestionPermissions
from Ontology.QuestionModule.upload_image import UploadImage
from UsersModule.users import Users
#from QuestionsModule.questions import Question, Questions, QuestionPermissions

##Create a superadmin

async def f():
    cursor = db["users"].find()
    async for doc in cursor:
        print(doc)

app_urls = [
			(r"/login", Login),
			(r"/signup$", Signup),
			(r"/signup/(\d+$)", Signup),
			(r"/signup/([a-zA-Z0-9_.-]*$)", Signup),
			(r"/users", Users),

			
			(r"/users$", Users),
			(r"/users/(\d+$)", Users),
			(r"/users/([a-zA-Z0-9_.-]*$)", Users),




            (r"/domains$", Domains),
            (r"/domainpermissions$", DomainPermissions),
			(r"/domainpermissions/([a-zA-Z0-9_.-]*$)", DomainPermissions),
			(r"/domains/([a-zA-Z0-9_.-]*$)", Domains),


            (r"/concepts$", Concepts),
			(r"/concepts/(\d+$)", Concepts),
			(r"/conceptpermissions/(\d+$)", ConceptPermissions),
			(r"/concepts/([a-zA-Z0-9_.-]*$)", Concepts),
            			


            (r"/subconcepts$", Subconcepts),
			(r"/subconcepts/(\d+$)", Subconcepts),
			(r"/subconceptpermissions/(\d+$)", SubconceptPermissions),
			(r"/concepts/([a-zA-Z0-9_.-]*$)", Subconcepts),



            (r"/nanoskills$", Nanoskills),
			(r"/nanoskills/(\d+$)", Nanoskills),
			(r"/nanoskillpermissions/(\d+$)", NanoskillPermissions),
			(r"/nanoskills/([a-zA-Z0-9_.-]*$)", Nanoskills),


            (r"/questions$", Questions),
            (r"/questionpermissions$", QuestionPermissions),
			(r"/questionpermissions/([a-zA-Z0-9_.-]*$)", QuestionPermissions),
			(r"/questions/([a-zA-Z0-9_.-]*$)", Questions),
			(r"/uploadimage$", UploadImage),


            #(r"/question$", Question),
            #(r"/questions$", Questions),
            #(r"/question/([a-zA-Z0-9_.-]*$)", Question),
            #(r"/questionpermissions$", QuestionPermissions),

			]



def handle_signal(sig, frame):
    loop = IOLoop.instance()
    logger.info("stopping server dude")
    loop.add_callback(loop.stop)
    
def make_indexes():
    print ("Making Domain Collcetion Indexes")
    try:
        mongo_db[domain_collection_name].create_index([("ngrams", motor.pymongo.TEXT), ("children", motor.pymongo.DESCENDING)])   
    except Exception as e:
        print (e)

    print ("Making Concept Collcetion Indexes")
    try:
        mongo_db[concept_collection_name].create_index([("ngrams", motor.pymongo.TEXT), ("children", motor.pymongo.DESCENDING)])   
    except Exception as e:
        print (e)

    print ("Making Subconcept Collcetion Indexes")
    try:
        mongo_db[subconcept_collection_name].create_index([("ngrams", motor.pymongo.TEXT), ("children", motor.pymongo.DESCENDING)])
    except Exception as e:
        print (e)
    
    print ("Making Nanoskill Collcetion Indexes")
    try:
        mongo_db[nanoskill_collection_name].create_index([("ngrams", motor.pymongo.TEXT), ("children", motor.pymongo.DESCENDING)])   
    except Exception as e:
        print (e)


    print ("Making Question Collcetion Indexes")
    try:
        mongo_db[question_collection_name].create_index([("ngrams", motor.pymongo.TEXT), ("children", motor.pymongo.DESCENDING)])   
    except Exception as e:
        print (e)

    print ("Making User Collection Indexes")
    try:
        mongo_db[user_collection_name].create_index([("ngrams", motor.pymongo.TEXT)])   
    except Exception as e:
        print (e)




if __name__ == "__main__":

        tornado.options.parse_command_line()
        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)
        app = tornado.web.Application(handlers=app_urls, db=mongo_db)
        http_server = tornado.httpserver.HTTPServer(app)
        http_server.listen(options.port)
        #asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        #AsyncIOMainLoop().install()
        #asyncio.get_event_loop().run_forever()
        logger.info("Application server started on %s"%options.port)
        make_indexes()
        IOLoop.instance().start()
