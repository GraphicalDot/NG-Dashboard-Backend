import tornado.options
import tornado.web
from tornado.escape import json_decode as TornadoJsonDecode
from SettingsModule.settings  import user_collection_name, indian_time, jwt_secret
from LoggingModule.logging import logger
import time 
import hashlib
from pprint import pprint
import jwt
import json
from AuthenticationModule.authentication import auth
#https://emptysqua.re/blog/refactoring-tornado-coroutines/
## finding user from motor  yields a future object which is nothing but a promise that it will have a value in future
## and gen.coroutine is a perfect to resolve a future object uyntillit is resolved

import codecs

from generic.cors import cors
reader = codecs.getreader("utf-8")



#@auth
class Users(tornado.web.RequestHandler):

	def initialize(self):
		self.db = self.settings["db"]
		self.collection = self.db[user_collection_name]
	
	
	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def options(self, domain_id=None):
        # no body
		self.set_status(204)
		self.finish()

	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def  post(self):
		if not self.request.body:
			raise Exception("Dude! I need some data")
		print (self.request.body)
		post_arguments = json.loads(self.request.body.decode("utf-8"))
		first_name = post_arguments.get("first_name")
		last_name = post_arguments.get("last_name")
		user_name = post_arguments.get("user_name")
		email = post_arguments.get("email")
		password = post_arguments.get("password")
		permissions = post_arguments.get("permissions", None)
		is_admin =  post_arguments.get("is_admin", False)
		phone_number = post_arguments.get("phone_number", None)
		user_type = post_arguments.get("user_type", None)
		
		##Permissions
		##For the user other 
		
		#user = yield db[credentials].find_one({'user_type': user_type, "username": username, "password": password})
		try:
			if user_type != "superadmin":
				raise Exception("Only superadmin can make users")

			##check if email is already registered with us
			user = yield self.collection.find_one({"email": email})
			if user:
				raise Exception("User Exists")

			_id = hashlib.sha1(email.encode("utf-8")).hexdigest()
			password= hashlib.sha1(password.encode("utf-8")).hexdigest()
			

			"""
			if category_permissions:
					a = CategoriesPermissions()
					yield a.update_permissions(self.db, user_id, category_permissions)
			"""
			user = {'first_name': first_name, "last_name": last_name,"user_name": user_name, \
							 "user_id": _id,"utc_epoch": time.time(), "indian_time": indian_time(), "email": email, 
							 "password": password, "is_admin": is_admin,
							 "permissions": permissions, "phone_number": phone_number
							 }

			yield self.collection.insert_one(user)

			logger.info("User created at %s with user_id %s"%(indian_time(), _id))
			
			
			
		

			#TODO: will be used to send email to the user
			##executor.submit(task, datetime.datetime.now())
		except Exception as e:
				logger.error(e)
				self.write({"error": True, "success": False, "token": None, "message": e.__str__()})
				self.finish()
				return 

		##This line has to be added, somehow while inserting nanoskill into the mongo, nanoskill itself got a new _id key
		##which is not serializable
		##TODO : implement JWT tokens
		user.pop("_id")
		self.write({"error": False, "success": True, "data": user})
		self.finish()
		return 




	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def put(self, user_id):
		##TODO if a user has to become a superadmin
		details = json.loads(self.request.body.decode("utf-8"))
		
		user = yield self.collection.find_one({"user_id": user_id}, projection={'_id': False})
		if user:
			logger.info(details)
			result = yield self.collection.update_one({'user_id': user_id}, {'$set': details})
			logger.info(result.modified_count)
			message = {"error": False, "success": True, "data": "User has been updated"}

		else:
				message = {"error": True, "success": False, "message": "User doesnt exist"}
		self.write(message)
		self.finish()
		return 

	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def delete(self, _id):
		result = yield self.collection.find_one({"user_id": _id}, projection={'_id': False})
		if result:
				result = yield self.collection.find_one_and_delete({'user_id': _id})
				logger.info(result)
				message = {"error": False, "success": True, "message": "User has been deleted"}
		else:
				message = {"error": True, "success": False, "message": "User doesnt exist"}

		#TODO: delete all parmissions as well
		self.write(message)
		self.finish()
		return

	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def get(self, _id=None):
		#user = self.check_user(user_id)
		if _id:
				result = yield self.collection.find({"user_id": user_id}, projection={'_id': False})
		else:
				_result = yield self.collection.find(projection={'_id': False}).to_list(length=100)
				object_ids = []
				objects = []
				for _object in _result:
					object_ids.append(_object.get("user_id"))
					objects.append(_object)
				result = {"users": objects,"user_ids": object_ids}


		if result:
				message = {"error": False, "success": True, "message": None, "data": result}

		else:
				message = {"error": True, "success": False, "message": "No user exist"}

		self.write(message)
		pprint(message)
		self.finish()
		return 



