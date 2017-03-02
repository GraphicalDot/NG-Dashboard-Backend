#!/usr/bin/env python3
import tornado.httpserver
from tornado.ioloop import IOLoop
import signal
import tornado.options
import tornado.web
import tornado.httpclient

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
from SignupModule.signup import Signup, SignupApplicant, Users
from SettingsModule.settings import mongo_db
from CategoryModule.categories import Category, Categories, CategoryPermissions
from CriteriaModule.criteria import Criteria, Criterion, CriteriaPermissions
from SubCriteriaModule.subcriteria import SubCriteria, SubCriterions, SubCriteriaPermissions
from LevelModule.levels import Level, Levels, LevelPermissions
from QuestionsModule.questions import Question, Questions, QuestionPermissions

app_urls = [
			(r"/login", Login),
			(r"/signup$", Signup),
			(r"/signup/(\d+$)", Signup),
			(r"/signup/([a-zA-Z0-9_.-]*$)", Signup),
			(r"/users", Users),

			(r"/signupapplicant$", SignupApplicant),
			(r"/signupapplicant/(\d+$)", SignupApplicant),
			(r"/signupapplicant/([a-zA-Z0-9_.-]*$)", SignupApplicant),
			

			#(r"/category$", Category),
			#(r"/categories$", Categories),
			#(r"/category/([a-zA-Z0-9_.-]*$)", Category),
			#(r"/categorypermissions$", CategoryPermissions),

            (r"/criteria$", Criteria),
            (r"/criterion$", Criterion),
            (r"/criteria/([a-zA-Z0-9_.-]*$)", Criteria),
            (r"/criteriapermissions$", CriteriaPermissions),



            (r"/subcriteria$", SubCriteria),
            (r"/subcriterion$", SubCriterions),
            (r"/subcriteria/([a-zA-Z0-9_.-]*$)", SubCriteria),
            (r"/subcategorypermissions$", SubCriteriaPermissions),


            (r"/level$", Level),
            (r"/levels$", Levels),
            (r"/level/([a-zA-Z0-9_.-]*$)", Level),
            (r"/levelpermissions$", LevelPermissions),
			
            (r"/question$", Question),
            (r"/questions$", Questions),
            (r"/question/([a-zA-Z0-9_.-]*$)", Question),
            (r"/questionpermissions$", QuestionPermissions),

			]



def handle_signal(sig, frame):
    loop = IOLoop.instance()
    logger.info("stopping server dude")
    loop.add_callback(loop.stop)


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

        IOLoop.instance().start()
