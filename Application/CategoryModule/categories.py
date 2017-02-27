



#!/usr/bin/env python3
from SettingsModule.settings import question_collection_name, default_document_limit,\
									indian_time, permissions, category_collection_name

from AuthenticationModule.authentication import auth
from tornado.web import asynchronous
from tornado.gen import coroutine
import tornado
from LoggingModule.logging import logger
import hashlib
import json
import traceback

@coroutine
def check_if_super(category_name, collection, user_id, rest_parameter, category_id=None):
	"""
	check if a user have the super user permission in the collection for the specifid category
	i.e his/her user_id is present in the "super_permissions", 
	if True: 
			Then this user_id can create more entries into this collection or any children of this category, 
	this method also checks if this user is superadmin for this application, 
	if True:
		he/she can do anything with this collection
	"""
	if user_id == "superadmin":
		logger.info("The user is superadmin for category [%s]"%category_id)
		return True

	##check if user_id has access to all this categories in this module
	user_permission = yield collection.find_one({"name": "super_permissions", "all": {"$in": [user_id]}}, projection={"_id": True})
	if user_permission:
		logger.info("The user_id [%s] has superadmin permissions for category=[%s]"%(user_id, category_id))
		return True

	else:
			permission = yield if_module_permission(category_name, collection, user_id, rest_parameter, category_id)
			if permission:
				logger.info("Some fucks happened and its returning True")
				return True
			else:

				logger.info("Some fucks happened")
				raise Exception("Insufficient permission for the user %s"%user_id)
				
	return 


@coroutine
def if_module_permission(category_name, collection, user_id, rest_parameter, category_id):
	"""
	This method checks if the user_id has permission for the specific category, sub category etc 
	in a particular module 

	the permission can be of four types, create, get, delete , put
	create is the permission if a user can create child category of this partiular category
	Args:
		rest_parameter: "get", "put", "create", "delete"

	"""
	user_permission = yield collection.find_one({"category_id": category_id}, \
		projection={"_id": False, user_id: True})
	logger.info(user_permission)

	try:
		if user_permission[user_id][rest_parameter]:
			logger.info("The user_id [%s] has [%s] permissions for this category [%s]"%(user_id, rest_parameter, category_id))
			return True
	except Exception:
			logger.info("The user_id [%s] doesnt have [%s] permissions for this category [%s]"%(user_id, rest_parameter, category_id))
			return False

	return 


@auth
class Category(tornado.web.RequestHandler):
	def initialize(self):
		self.db = self.settings["db"]
		self.collection = self.db[category_collection_name]	

	@asynchronous
	@coroutine
	##@categoryauth
	def post(self):
			"""
			for each category scema

				category_id:
				category_name: 
				score:
				super: list of ids who have access to all crud operation for this category id
				create:
				delete:
				get:

			A user_id must be present in {"all": []} list which implies that this user_id can do anything with this
			collection
			If an existing  category is to be edited then put request must be used
			
			#TODO: check if a user has create permission for this category, which implies that this user_id
					has create permission for its parent_id
			"""
			#permissions = {"create": False, "delete": False, "edit": False, "get": False}
			post_arguments = json.loads(self.request.body.decode("utf-8"))
			category_name = post_arguments.get("category_name", None)
			text_description = post_arguments.get("text_description", None)
			score = post_arguments.get("text_description", None)
			user_id = post_arguments.get("user_id", None) ##who created this category
			user_permission = yield self.collection.find_one({"name": "super_permissions", "all": {"$in": [user_id]}}, projection={"_id": True})
			permissions = post_arguments.get("permissions", None)

			logger.info(post_arguments)
			try:
					# if not user_permission:
					# 	if user_id == "superadmin":
					# 		pass
					# 	else:
					# 		raise Exception("Insufficient permission for this user")
					yield check_if_super(category_name, self.collection, user_id, "post", None)

					category = yield self.collection.find_one({"category_name": category_name})
					if category:
						raise Exception("%s category already exists"%(category_name))

					category_hash = "%s%s"%(user_id, category_name)

					category_id = hashlib.sha1(category_hash.encode("utf-8")).hexdigest()
					category = yield self.collection.insert_one({"category_id": category_id, "category_name": category_name, 
							"user_id": user_id, "score": score, "text_description": text_description})
					logger.info("New category with name %s and _id=%s created"%(category_name, category.inserted_id))

					if permissions:
						for permission in permissions["ids"]:
							##the _id is th eids of the other user to whom used_id wants to provide permissions
							_id = permission.pop("id")
							update = yield self.collection.update_one({"category_id": category_id}, \
													{"$set": {_id: permission}}, upsert=True)
							logger.info(update)
					
					##this will add the creator id crud operation permission to this category
					update = yield self.collection.update_one({"category_id": category_id}, \
											{"$set": {user_id: {"create": True, "delete": True, "update": True, "get": True}}}, upsert=True)

			except Exception as e:
				logger.error(e)
				self.write({"error": True, "success": False, "message": e.__str__()})
				self.finish()
				return 
			self.write({"error": False, "success": True, "category_name": category_name, "category_id": category_id})
			self.finish()
			return 
			


	@asynchronous
	@coroutine
	##allowed roles is user who has been assigned this category and admin
	def get(self, category_id):
			get_arguments = json.loads(self.request.body.decode("utf-8"))
			user_id = get_arguments.get("user_id", None) ##who created this category
			#user_permission = yield self.collection.find_one({"name": "super_permissions", "all": {"$in": [user_id]}}, projection={"_id": True})
			try:
				yield check_if_super(None, self.collection, user_id, "get", category_id)

				# check_if_super(categroy_id, self.collection, user_id, "get")
				# 	if not user_permission:
				# 		if user_id == "superadmin":
				# 			pass
				# 		else:
				# 			user_permission = yield self.collection.find_one({"category_id": category_id},\
				# 			 projection={"_id": False, user_id: True})
				# 			logger.info(user_permission)
				# 			if user_permission[user_id]["get"]:
				# 					category = yield self.collection.find_one({"category_id": category_id}, projection={"_id": False})
				# 			else:
				# 				raise Exception("Insufficient permission for this user")
				category = yield self.collection.find_one({"category_id": category_id}, projection={"_id": False})
			except Exception as e:
				print (traceback.format_exc())
				logger.error(e)
				self.write({"error": True, "success": False, "message": e.__str__()})
				self.finish()
				return 
			self.write({"error": False, "success": True, "category": category})
			self.finish()
			return 


	@asynchronous
	@coroutine
	def put(self, category_id):
			"""
			This will be used to change text desciption, overall score only by the superadmin, 
			and the user who created it, and the user who have been allowed to do so
			"""
			post_arguments = json.loads(self.request.body.decode("utf-8"))
			
			text_description = post_arguments.get("text_description", None)
			score = post_arguments.get("text_description", None)
			user_id = post_arguments.get("user_id", None) ##who created this category
			user_permission = yield self.collection.find_one({"name": "super_permissions", "all": {"$in": [user_id]}}, projection={"_id": True})
			permissions = post_arguments.get("permissions", None)
			try:
					yield check_if_super(None, self.collection, user_id, "put", category_id)
					
					# if not user_permission:
					# 	if user_id == "superadmin":
					# 		pass
					# 	else:
					# 		user_permission = yield self.collection.find_one({"category_id": category_id},\
					# 		 projection={"_id": False, user_id: True})
					# 		logger.info(user_permission)
					# 		if user_permission[user_id]["update"]:
					# 				pass
					# 		else:
					# 			raise Exception("Insufficient permission for this user")

					if permissions:
						logger.info(permissions)
						for permission in permissions["ids"]:
							_id = permission.pop("id")
							update = yield self.collection.update_one({"category_id": category_id}, \
													{"$set": {_id: permission}}, upsert=True)
							logger.info(update)

					self.collection.update_one({"category_id": category_id}, {"$set":{"text_description": text_description,\
						"score": score}}, upsert=False)					

			except Exception as e:
				print (traceback.format_exc())
				logger.error(e)
				self.write({"error": True, "success": False, "message": e.__str__()})
				self.finish()
				return 
			self.write({"error": False, "success": True, "category_id": category_id})
			self.finish()
			return 



	@asynchronous
	@coroutine
	def delete(self, category_id):
			"""
			Only the superadmin and the admin who created it will be able to delete this category
			And also the user who have been given persmissions to do so.
			"""
			post_arguments = json.loads(self.request.body.decode("utf-8"))
			user_id = post_arguments.get("user_id", None) ##who created this category
			user_permission = yield self.collection.find_one({"name": "super_permissions", "all": {"$in": [user_id]}}, projection={"_id": True})
			try:
					yield check_if_super(None, self.collection, user_id, "delete", category_id)
				
					# if not user_permission:
					# 	if user_id == "superadmin":
					# 		pass
					# 	else:
					# 		user_permission = yield self.collection.find_one({"category_id": category_id},\
					# 		 projection={"_id": False, user_id: True})
					# 		logger.info(user_permission)
					# 		if user_permission[user_id]["delete"]:
					# 				yield self.collection.delete_one({"category_id": category_id})
									
					# 		else:
					# 			raise Exception("Insufficient permission for this user")
			except Exception as e:
				print (traceback.format_exc())
				logger.error(e)
				self.write({"error": True, "success": False, "message": e.__str__()})
				self.finish()
				return 
			self.write({"error": False, "success": True, "category_id": category_id})
			self.finish()
			return 



class Categories(tornado.web.RequestHandler):
	"""
	Return questions 
	Questions can filtered according to the 
		admin created id
		superadmin id
		category id
		date created	
	"""

	def initialize(self):
		self.db = self.settings["db"]
		self.collection = self.db[category_collection_name]	



	@asynchronous
	@coroutine
	def get(self, limit=None, skip=None, admin_id=None, category_id=None, sub_category_id=None, date_created=None):
		limit = self.get_argument("limit", None)
		skip = self.get_argument("skip", None)

		if not limit:
			limit = default_document_limit
		if not skip:
			skip = 0


		pass


class CategoriesPermissions(object):

	@coroutine
	def update_permissions(self, db, user_id, permission_dict):
		"""
		permission_dict will have two keys
		"super": True
				this implies that this user can do crud operations on this collection i.e category_collection
		so the categories collection will have a super_permissions entry in which there will be an "all" key
		which will have a list of all the user_ids who can do anything with this collection

		permission list will be a list of dict, with each dict is of the form
		{"id": , "create": True, "edit": True, "delete": True, "update": True}

		First check if category_id exists or not, 



		"""
		logger.info("categories permissions function has been called")
		if permission_dict["super"]:
			super_permissions = yield db[category_collection_name].update_one({"name": "super_permissions"},  {"$addToSet": { "all": user_id }}, upsert=True)
		else:
			for permission in permission_dict["ids"]:
				_id = permission.pop("id")
				update = yield db[category_collection_name].update_one({"category_id": id}, {"$set": {user_id: permission}}, upsert=True)
				logger.info(update)
		return 


	@staticmethod
	def get_permissions(self, db, user_id):
			return 












