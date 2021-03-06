import tornado.options
import tornado.web
from tornado.escape import json_decode as TornadoJsonDecode
from SettingsModule.settings  import user_collection_name, indian_time, jwt_secret, \
									 default_document_limit
from LoggingModule.logging import logger
import time 
import hashlib
import jwt
import json
from AuthenticationModule.authentication import auth
#https://emptysqua.re/blog/refactoring-tornado-coroutines/
## finding user from motor  yields a future object which is nothing but a promise that it will have a value in future
## and gen.coroutine is a perfect to resolve a future object uyntillit is resolved

import codecs

reader = codecs.getreader("utf-8")


@auth
class Users(tornado.web.RequestHandler):

	def initialize(self):
		self.db = self.settings["db"]
		self.collection = self.db[user_collection_name]	


	
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def  post(self):
		post_arguments = json.loads(self.request.body.decode("utf-8"))
		user_id = post_arguments.get("user_id") 
		skip = post_arguments.get("skip", 0) 
		limit = post_arguments.get("limit", default_document_limit) 

		try:
			assert isinstance(skip, int), "skip must be an int"
			assert isinstance(limit, int), "limit must be an int"
			user = yield self.collection.find_one({"user_id": user_id})

			if not user:
					raise Exception("User doesnt exist, Please signup first")

			if user["user_type"] == "superadmin":
					##give away alll the users
					users = yield self.collection.find({"parent_user_id": {"$ne": user_id}}, projection={"_id": False}).\
					skip(skip).sort([('indian_time', -1)]).to_list(length=limit)
					logger.info(users)

			if user["user_type"] == "admin":
					logger.info("Users request is from admin user")
					users = yield self.collection.find({"parent_user_id": user_id}, projection={"_id": False}).skip(skip)\
					.sort([('indian_time', -1)]).to_list(length=limit)
					logger.info(users)

		except Exception as e:
				logger.error(e)
				self.write({"error": True, "success": False, "token": None, "message": e.__str__()})
				self.finish()
				return 

		##TODO : implement JWT tokens
		self.write({"error": False, "success": True, "users": users})
		self.finish()
		return 



@auth
class Signup(tornado.web.RequestHandler):

	def initialize(self):
		self.db = self.settings["db"]
		self.collection = self.db[user_collection_name]	


	
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def  post(self):
		"""
		Used to create a new user or update and existing one
		Request Param:
			user_type: admin, accessor, evaluator, superadmin
			username: 
			password: 

		When creating the admin, The superadmin can grant access to the admin user whether he can 
		crud category, subcategory, level or question
		if all permissions are aloowed on all four, then he is super: True
		else:
			super admin can select multiple categories, multiple sub categories, and levels
			from the dropdpwn, now instead of super, following ids will be pushed to the 
			dict permissions for corresponding category_permissions, sub_category_permissions
			or level_permissions, all these also have crud operations ids in them 

			Also to be safe, all the categories, sub categories and levels have list of user ids 
			pushed into crud operations

		"""
		post_arguments = json.loads(self.request.body.decode("utf-8"))
		user_type = post_arguments.get("user_type")
		first_name = post_arguments.get("full_name", None)
		last_name = post_arguments.get("last_name", None)
		email = post_arguments.get("email", None)
		username = post_arguments.get("username", None)
		password = post_arguments.get("password", None)
		phone_number = post_arguments.get("phone_number", None)
		##Permissions
		##For the user other 
		deactivate = post_arguments.get("deactivate", None)

		
		logger.info("user_type=%s, first_name=%s, user_email=%s, username=%s, \
			password=%s, phone_number=%s "%(user_type, first_name, email,\
			  username, password, phone_number))


		
		#user = yield db[credentials].find_one({'user_type': user_type, "username": username, "password": password})
		
		try:
			if None in [user_type, username, password, email, first_name]:
				raise Exception("Fields shouldnt be empty")


			parent =  yield self.collection.find_one({"user_id": parent_user_id})
			logger.info(parent)
			if not parent:
				raise Exception("Parent id doesnt exist, cant create this user")

			if is_superadmin and parent["user_type"] != "superadmin":
				raise Exception("Only superadmin can create superadmin")

			if parent["user_type"] == "admin" and user_type == "admin":
				raise Exception("Only superadmin can create admin, admin cant create admin ")




			##check if email is already registered with us
			user = yield self.collection.find_one({"email": email})
			if user:
				raise Exception("This email id have already been registered with us")

			user_id = hashlib.sha1(email.encode("utf-8")).hexdigest()
			password = hashlib.sha1(password.encode("utf-8")).hexdigest()


			"""
			if category_permissions:
					a = CategoriesPermissions()
					yield a.update_permissions(self.db, user_id, category_permissions)
			"""
			user = yield self.collection.insert_one({'user_type': user_type, "username": username,\
							 "password": password, "region": region, "state": state,\


							  "email": email, "profile_pic": profile_pic, "utc_epoch": time.time(), "indian_time": indian_time(), "user_id": user_id, 
							  "is_superadmin": is_superadmin, "parent_user_id": parent_user_id, "deactivate": deactivate})

			logger.info("User added at %s with user_id %s"%(indian_time(), user_id))
			
			
			
		
			#TODO: will be used to send email to the user
			##executor.submit(task, datetime.datetime.now())
		except Exception as e:
				logger.error(e)
				self.write({"error": True, "success": False, "token": None, "message": e.__str__()})
				self.finish()
				return 

		##TODO : implement JWT tokens
		logger.info("This is the password %s"%password)
		token =  jwt.encode({'username': username, "password": password, "user_type": user_type}, jwt_secret, algorithm='HS256')
		self.write({"error": False, "success": True, "token": token.decode("utf-8"), "user_id": user_id})
		self.finish()
		return 



	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def put(self, user_id):
		##TODO if a user has to become a superadmin
		user = yield self.collection.find_one({"user_id": user_id}, projection={'_id': False})
		if user:
				details = { k: self.get_argument(k) for k in self.request.arguments if k not in ["state", "region"]}

				state = self.request.arguments.get("state")
				region = self.request.arguments.get("region") 

				if state:
						state =  list(map(lambda x: x.decode("utf-8"), state))
						details["state"] = state
				if region:
						region = list(map(lambda x: x.decode("utf-8"), region)) 
						details["region"] = region

				if not bool(details):
						message = {"error": True, "success": False, "message": "Nothing to update"}
						self.write(message)
						self.finish()
						return 
						

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

		#TODO: delete all parmissions as well
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




# This class will be used when the applicant needs to do the registration, here auth is not
# required because any applicant can change its application

class SignIn(tornado.web.RequestHandler):
	def initialize(self):
		self.db = self.settings["db"]
		self.collection = self.db[user_collection_name]	



	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def post(self):
		post_arguments = json.loads(self.request.body.decode("utf-8"))
		username = post_arguments.get("username")
		password = post_arguments.get("password")
		try:
			if None in [password, username]:
				raise Exception("Fields shouldnt be empty")
				
			user = yield self.collection.find_one({"username": username, "password": password}, projection={"_id": False, "phone_number": False, 
																				"permissions": False, "indian_time": False, "utc_epoch": False})
			
			if not user:
					raise Exception("This user doesnt exists")
			
			

			token =  jwt.encode({'username': username, "password": password, "user_type": user["user_type"]}, jwt_secret, algorithm='HS256')
		except Exception as e:
				logger.error(e)
				self.write({"error": True, "success": False, "token": None, "message": e.__str__()})
				self.finish()
				return 

		##This line has to be added, somehow while inserting nanoskill into the mongo, nanoskill itself got a new _id key
		##which is not serializable
		##TODO : implement JWT tokens
		user.pop("_id")
		self.write({"error": False, "success": True, "data": user, "token": token.decode("utf-8")})
		self.finish()
		return 





	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def get(self, user_id):
			pass


	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def put(self, user_id):
			pass

	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def post(self, user_id):
			pass

	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def delete(self, user_id):
			pass



