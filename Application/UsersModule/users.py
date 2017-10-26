import tornado.options
import tornado.web
from tornado.escape import json_decode as TornadoJsonDecode
from SettingsModule.settings  import domain_collection_name, indian_time, jwt_secret,\
									default_document_limit, user_collection_name, permission_collection_name,\
									 action_collection_name, concept_collection_name, subconcept_collection_name,\
									 nanoskill_collection_name, question_collection_name
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
import math
from GeneralModule.cors import cors
reader = codecs.getreader("utf-8")





#@auth
class Users(tornado.web.RequestHandler):

	def initialize(self):
		self.db = self.settings["db"]
		self.collection = self.db[user_collection_name]
		self.domain_collection = self.db[domain_collection_name]
		self.concept_collection = self.db[concept_collection_name]
		self.subconconcept_collection = self.db[subconcept_collection_name]
		self.nanoskill_collection = self.db[nanoskill_collection_name]
		self.question_collection = self.db[question_collection_name]
		self.permission_collection = self.db[permission_collection_name]

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
		username = post_arguments.get("username", None)
		email = post_arguments.get("email")
		password = post_arguments.get("password")
		permissions = post_arguments.get("permissions", None)
		phone_number = post_arguments.get("phone_number", None)
		user_type = post_arguments.get("user_type", None)
		create_domain = post_arguments.get("create_domain", None)
		user_secret = post_arguments.get("user_secret", None)
		create_variable = post_arguments.get("create_variable", None)
		create_variabletemplate = post_arguments.get("create_variabletemplate", None)
		create_template = post_arguments.get("create_template", None)
		##Permissions
		##For the user other 

		pprint (post_arguments)		
		#user = yield db[credentials].find_one({'user_type': user_type, "username": username, "password": password})
		try:
			if None in [user_secret, username,  email ]:
				raise Exception("Fields shouldnt be empty")
				
			if user_secret != jwt_secret:
				raise Exception("your secret is wrong")
				

			##check if email is already registered with us
			user = yield self.collection.find_one({"email": email})
			if user:
				raise Exception("User Exists")

			_id = hashlib.sha256(email.encode("utf-8")).hexdigest()
			password=hashlib.sha256(password.encode("utf-8")).hexdigest()

			##This is because i have made the rest of the code for general purpose user as False for checking
			"""
			if user_type == "general":
				user_type = False			

			if category_permissions:
					a = CategoriesPermissions()
					yield a.update_permissions(self.db, user_id, category_permissions)
			"""
			user = {'first_name': first_name, "last_name": last_name,"username": username, \
							 "user_id": _id,"utc_epoch": time.time(), "indian_time": indian_time(), "email": email, 
							 "password": password, "user_type": user_type,
							 "permissions": permissions, "phone_number": phone_number, "create_domain": create_domain,
							 "ngrams": " ".join(self.make_ngrams(username) + self.make_ngrams(email) + self.make_ngrams(first_name) + self.make_ngrams(last_name)),
							"create_template": create_template, "create_variable": create_variable, "create_variabletemplate": create_variabletemplate,
							 }

			yield self.collection.insert_one(user)


			#TODO: will be used to send email to the user
			##executor.submit(task, datetime.datetime.now())
		except Exception as e:
				logger.error(e)
				self.set_status(403)
				self.write( e.__str__())
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
	def put(self):
		##TODO if a user has to become a superadmin
		details = json.loads(self.request.body.decode("utf-8"))
		pprint (details)
		user = yield self.collection.find_one({"user_id": details["user_id"]}, projection={'_id': False})
		if user:
			logger.info(details)
			result = yield self.collection.find_and_modify({'user_id': details["user_id"]}, {'$set': details})
			logger.info(result)
			message = {"error": False, "success": True, "message": "User with username %s has been updated"%user["username"], "data": details}

		else:
				message = {"error": True, "success": False, "message": "User doesnt exist"}
		self.write(message)
		self.finish()
		return 

	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def delete(self):
		# Only superadmin can delete the user, And after deletion all the ownership of all kinds passed to 
		## superadmin
		
		print (self.request.headers)
		print (self.request.arguments)
		print (self.request.body)
		user_id = self.request.arguments.get("user_id")[0].decode("utf-8")
		action_user_id = self.request.arguments.get("action_user_id")[0].decode("utf-8")

		print (action_user_id)
		print (user_id)
		try:
			if not action_user_id:
				raise Exception("Please send the user_id of person who wants to delete")

			user = yield self.collection.find_one({"user_id": action_user_id}, projection={'_id': False})
			if user["user_type"] != "superadmin":
				raise Exception ("Only superadmins can delete users")

			print (user)
			result = yield self.collection.find_one({"user_id": user_id}, projection={'_id': False})
			if result:
				result = yield self.collection.find_one_and_delete({'user_id': user_id})
				yield self.domain_collection.update_many({"user_id": user_id}, {"$set": {"user_id": action_user_id}}, upsert=False)
				yield self.concept_collection.update_many({"user_id": user_id}, {"$set": {"user_id": action_user_id}}, upsert=False)
				yield self.subconconcept_collection.update_many({"user_id": user_id}, {"$set": {"user_id": action_user_id}}, upsert=False)
				yield self.nanoskill_collection.update_many({"user_id": user_id}, {"$set": {"user_id": action_user_id}}, upsert=False)
				yield self.question_collection.update_many({"user_id": user_id}, {"$set": {"user_id": action_user_id}}, upsert=False)
				yield self.permission_collection.delete_many({"user_id": user_id})
				yield self.permission_collection.update_many({"granter_id": user_id}, {"$set": {"granter_id": action_user_id}}, upsert=False)



				logger.info(result)
				message = {"error": False, "success": True, "message": "User has been deleted"}
			else:
				raise Exception ("No user Exists")

			message = {"error": False, "success": True, "data": user_id}
		except Exception as e:
			logger.error(str(e.__str__()))
			self.set_status(400)
			message = {"error": True, "success": False, "data": str(e.__str__())}


		#TODO: delete all parmissions as well
		self.write(message)
		self.finish()
		return

	def make_ngrams(self, word, min_size=2):
		"""
		basestring       word: word to split into ngrams
		int   min_size: minimum size of ngrams
		"""
		length = len(word)
		size_range = range(min_size, max(length, min_size) + 1)
		return list(set(
			word[i:i + size]
			for size in size_range
			for i in range(0, max(0, length - size) + 1)
			))


	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def get(self):
		#user = self.check_user(user_id)
		print (self.request.arguments)
		try:
			skip = self.request.arguments.get("skip")[0].decode("utf-8")
			skip = int(skip)
		except Exception as e:
			skip = 0

		try:
			limit = self.request.arguments.get("limit")[0].decode("utf-8")
			limit = int(limit)
		except Exception as e:
			limit = 0
		
		try:
			search_text = self.request.arguments.get("search_text")[0].decode("utf-8")
		except Exception as e:
			search_text = None

		
		try:
			user_id = self.request.arguments.get("user_id")[0].decode("utf-8")
		except Exception as e:
			raise Exception("User id required")
		


		users_result = []
		user = yield self.collection.find_one({"user_id": user_id}, projection={"_id": False, "ngrams": False})
		try:

			if search_text:
				count = yield self.collection.find({"$text":{"$search": search_text}}, projection={"_id": False, "ngrams": False}).count()
				cursor = self.collection.find({"$text":{"$search": search_text}}, 
							projection={"_id": False, "ngrams": False}).skip(skip).limit(limit)
				while (yield cursor.fetch_next):
					users_result.append(cursor.next_object())
			else:
				
				cursor = self.collection.find(projection={'_id': False, "ngrams": False}).skip(skip).limit(limit)
				count = yield self.collection.find(projection={'_id': False, "ngrams": False}).count()
				while (yield cursor.fetch_next):
					users_result.append(cursor.next_object())
							

			user_ids = []
			users = []

			##Now the filtering part, A user shall not be shown its her own record.
			## A general or admin shall not be shown superadmin record.
			## A general user shouldnt be shown admin or superadmin record
			for _object in users_result:
				if not _object.get("user_id") == user_id:
					if user["user_type"] != "superadmin" or user["user_type"] != "admin":
						if not _object.get("user_type") == "superadmin" or not _object.get("user_type") == "admin":
							user_ids.append(_object.get("user_id"))
							users.append(_object)
					elif user["user_type"] == "admin": 
						if _object.get("user_type") == "admin":
							user_ids.append(_object.get("user_id"))
							users.append(_object)
					elif user["user_type"] == "superadmin": 
						if _object.get("user_type") == "superadmin":
							user_ids.append(_object.get("user_id"))
							users.append(_object)


			result = {"users": users,"user_ids": user_ids}
			result.update({"user_count": count, "pages":  math.ceil(count/limit)})

			pprint (result)
			message = {"error": False, "success": True, "message": None, "data": result}

		except Exception as e:
				logger.error(e)
				self.set_status(400)
				self.write( e.__str__())
				self.finish()
				return 
	
		self.set_status(200)
		self.write(message)
		self.finish()
		return 



