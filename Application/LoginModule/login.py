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
		newpassword = post_arguments.get("newpassword", None)
		logger.info("username=%s, password=%s, newpassword=%s"%(username, password, newpassword))

		
		db = self.settings["db"]
		#user = yield db[credentials].find_one({'user_type': user_type, "username": username, "password": password})
		
		try:
			if not username or not password:
				raise Exception("username and password must be given")


			password = hashlib.sha1(password.encode("utf-8")).hexdigest()
			print (password)
			print (self.collection)
			user = yield self.collection.find_one({"username": username, "password": password})
			print (user)
			if not user:
				raise Exception("user doesnt exist")
			token =  jwt.encode({'username': user["username"], "password": user["password"]}, jwt_secret, algorithm='HS256')
			
		
		except Exception as e:
				logger.error(e)
				self.write({"error": True, "success": True, "token": None, "message": e.__str__()})
				#self.write({"error": False, "success": True})
				self.finish()
				return 

		self.write({"error": False, "success": True, "token": token.decode("utf-8"), "user_id": user.get("user_id")})
		self.finish()
		return 


