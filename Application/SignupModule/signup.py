import tornado.options
import tornado.web


import sys
from os.path import dirname, abspath
parentdir = dirname(dirname(abspath(__file__)))
sys.path.append(parentdir)
from settings import credential_collection_name, indian_time, jwt_secret
from custom_logging import logger
import time 
import hashlib
import jwt
#https://emptysqua.re/blog/refactoring-tornado-coroutines/
## finding user from motor  yields a future object which is nothing but a promise that it will have a value in future
## and gen.coroutine is a perfect to resolve a future object uyntillit is resolved
class Signup(tornado.web.RequestHandler):

	def initialize(self):
		self.db = self.settings["db"]
		self.collection = self.db[credential_collection_name]	


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
		user_type = self.get_argument("user_type", None)
		full_name = self.get_argument("full_name", None)
		email = self.get_argument("email", None)
		username = self.get_argument("username", None)
		password = self.get_argument("password", None)
		state = self.get_argument("state", None)
		region = self.get_argument("region", None)
		profile_pic = self.get_argument("profile_pic", None)


		logger.info("user_type=%s, full_name=%s, user_email=%s, username=%s, \
			password=%s, state=%s, region=%s"%(user_type, full_name, email,\
			  username, password, state, region))

		
		#user = yield db[credentials].find_one({'user_type': user_type, "username": username, "password": password})
		
		try:
			if None in [user_type, username, password, email, state, region, full_name]:
				raise Exception("Fields shouldnt be empty")

			##check if email is already registered with us
			user = yield self.collection.find_one({"email": email})
			if user:
				raise Exception("This email id have already been registered with us")

			user_id = hashlib.sha1(email.encode("utf-8")).hexdigest()
			user = yield self.collection.insert_one({'user_type': user_type, "username": username,\
							 "password": password, "region": region, "state": state, "email": email, \
							 "profile_pic": profile_pic, "utc_epoch": time.time(), "indian_time": indian_time(), "user_id": user_id })
			
			logger.info("User added at %s with user_id %s"%(indian_time(), user_id))
		
			#TODO: will be used to send email to the user
			##executor.submit(task, datetime.datetime.now())
		except Exception as e:
				logger.error(e)
				self.write({"error": False, "success": True, "token": None, "message": e.__str__()})
				self.finish()
				return 

		##TODO : implement JWT tokens
		token =  jwt.encode({'username': username, "password": password, "email": email}, 'secret', algorithm='HS256')
		self.write({"error": False, "success": True, "token": token.decode("utf-8")})
		self.finish()
		return 



	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def put(self, user_id):
		user = yield self.collection.find_one({"user_id": user_id}, projection={'_id': False})
		if user:
				details = self.request.arguments
				logger.info(details)
				result = yield self.collection.update_one({'user_id': user_id}, {'$set': details})
				logger.info(result.modified_count)
				message = {"error": False, "success": True, "message": "User has been updated"}

		else:
				message = {"error": True, "success": False, "message": "User doesnt exist"}
		self.write(message)
		self.finish()

		return 


	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def delete(self, user_id):
		user = yield self.collection.find_one({"user_id": user_id}, projection={'_id': False})
		if user:
				result = yield self.collection.find_one_and_delete({'user_id': user_id})
				logger.info(result)
				message = {"error": False, "success": True, "message": "User has been deleted"}
		else:
				message = {"error": True, "success": False, "message": "User doesnt exist"}

		self.write(message)
		self.finish()
		return

	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def get(self, user_id):
		#user = self.check_user(user_id)
		user = yield self.collection.find_one({"user_id": user_id}, projection={'_id': False})
		
		if user:
				message = {"error": False, "success": True, "message": None, "user": user}

		else:
				message = {"error": True, "success": False, "message": "User doesnt exist"}

		self.write(message)
		self.finish()
		return 
