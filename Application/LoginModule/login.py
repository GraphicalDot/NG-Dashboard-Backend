import tornado.options
import tornado.web
from SettingsModule.settings import user_collection_name, jwt_secret
from LoggingModule.logging import logger
from tornado.ioloop import IOLoop
import hashlib
import jwt
import json 
from pprint import pprint 

#https://emptysqua.re/blog/refactoring-tornado-coroutines/
## finding user from motor  yields a future object which is nothing but a promise that it will have a value in future
## and gen.coroutine is a perfect to resolve a future object uyntillit is resolved

from generic.cors import cors


class Login(tornado.web.RequestHandler):

	def initialize(self):
			self.db = self.settings["db"]
			self.collection = self.db[user_collection_name]

	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def  get(self):
		self.write({"error": False, "success": True})
		self.finish()
		return 



			
	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def  post(self):
		"""
		Used to create a new user or update and existing one
		Request Param:
			user_type: admin, accessor, evaluator, superadmin
			username: 
			password: 
			newpassword:
		"""

		print (self.request.body)
		post_arguments = json.loads(self.request.body.decode("utf-8"))
		print (post_arguments)
		username = post_arguments.get("username", None)
		password = post_arguments.get("password", None)

		
		#user = yield db[credentials].find_one({'user_type': user_type, "username": username, "password": password})
		
		try:
			if not username or not password:
				raise Exception("username and password must be given")


			user = yield self.collection.find_one({"username": username, "password": password}, projection={"_id": False, "phone_number": False, 
																				"permissions": False, "indian_time": False, "utc_epoch": False})
			if not user:
				raise Exception("user doesnt exist")
			token =  jwt.encode({'username': user["username"], "password": user["password"]}, jwt_secret, algorithm='HS256')
			user.update({"token": token.decode("utf-8")})
		
		except Exception as e:
				logger.error(e)
				self.set_status(401)
				pprint ({"error": True, "success": True, "token": None, "data": {"error": e.__str__()}})
				self.write( e.__str__())
				#self.write({"error": False, "success": True})
				self.finish()
				return 

		message = {"error": False, "success": True, "data": {"user": user, "token":token.decode("utf-8") }}
		pprint (message)
		self.write(message)
		self.finish()
		return 


