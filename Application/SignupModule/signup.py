import tornado.options
import tornado.web
from tornado.escape import json_decode as TornadoJsonDecode
from SettingsModule.settings  import user_collection_name, indian_time, jwt_secret, \
									user_types, permissions, question_collection_name,\
									category_collection_name, sub_category_collection_name, \
									level_collection_name, default_document_limit
from LoggingModule.logging import logger
import time 
import hashlib
import jwt
import json
from AuthenticationModule.authentication import auth
#https://emptysqua.re/blog/refactoring-tornado-coroutines/
## finding user from motor  yields a future object which is nothing but a promise that it will have a value in future
## and gen.coroutine is a perfect to resolve a future object uyntillit is resolved
from CategoryModule.categories import CategoriesPermissions
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
		self.categorie_collection = self.db[category_collection_name]
		self.level_collection = self.db[level_collection_name]
		self.sub_category_collection = self.db[sub_category_collection_name]
		self.question_collection = self.db[question_collection_name]


	
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
		full_name = post_arguments.get("full_name", None)
		email = post_arguments.get("email", None)
		username = post_arguments.get("username", None)
		password = post_arguments.get("password", None)
		state = post_arguments.get("state", None) 
		region = post_arguments.get("region", None) 
		profile_pic = post_arguments.get("profile_pic", None)
		##Permissions
		##For the user other 
		is_superadmin = post_arguments.get("is_superadmin", False) #handle this
		parent_user_id = post_arguments.get("parent_user_id", None) ## Which implies a superadmin

		
		logger.info("user_type=%s, full_name=%s, user_email=%s, username=%s, \
			password=%s, state=%s, region=%s,parent_user_id=%s, is_superadmin=%s "%(user_type, full_name, email,\
			  username, password, state, region, parent_user_id, is_superadmin))


		
		#user = yield db[credentials].find_one({'user_type': user_type, "username": username, "password": password})
		
		try:
			assert isinstance(state, list), "state permissions must be and array"
			assert isinstance(region, list), "region permissions must be and array"

			if None in [user_type, username, password, email, state, region, full_name]:
				raise Exception("Fields shouldnt be empty")

			if user_type not in user_types:
				raise Exception("user_type is not allowed")


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
							  "is_superadmin": is_superadmin, "parent_user_id": parent_user_id })

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

class SignupApplicant(tornado.web.RequestHandler):
	def initialize(self):
		self.db = self.settings["db"]
		self.collection = self.db[credential_collection_name]	

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



