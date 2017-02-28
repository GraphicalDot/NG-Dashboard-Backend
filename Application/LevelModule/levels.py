



#!/usr/bin/env python3
from SettingsModule.settings import question_collection_name, default_document_limit,\
									indian_time, permissions, category_collection_name,\
									app_super_admin, app_super_admin_pwd, app_super_admin_user_id,\
									user_collection_name, sub_category_collection_name, \
									indian_time, sub_criteria_collection_name, level_collection_name

from AuthenticationModule.authentication import auth
from tornado.web import asynchronous
from tornado.gen import coroutine
import tornado
from LoggingModule.logging import logger
import hashlib
import json
import traceback
import os.path import abspath
module_name = abspath(__file__)

@coroutine
def if_create_permissions(user_collection, parent_collection, child_collection, \
													user_id, rest_parameter, parent_id):
	"""
	If a user want to create a SubCategory

	superadmin can create anything
	The user must have get and create permission on parent category

	when created the user will have all permissions on this sub category
	"""

	parent = yield parent_collection.find_one({"parent_id": parent_id})
	if not parent:
			raise Exception("The parent with id=[%s] doesnt exists"%parent_id)

	user = yield user_collection.find_one({"user_id": user_id}, projection={"_id": False, "user_type": True})
	if not user:
			raise Exception("User doesnt exists")
	##Check if a user is superadmin
	if user["user_type"] == "superadmin":
			##returning whole parent document, which will be used to extract necessary information
			return parent 

	if not parent[user_id]:
			raise Exception("The userid= [%s] doesnt have permissions to create children on \
				parent with parent_id=[%s]"%(user_id, parent_id))



	##We dont have to check for get permissions has the userid cant see it, unless have
	##get permission on this subcategory
	if not parent.get(user_id).get(rest_parameter, None):
			raise Exception("The userid= [%s] doesnt have %s permissions to on parent  \
				with parent id=[%s] doesnt exists"%(user_id, rest_parameter, parent_id))

	return parent
								   


@coroutine
def if_module_permission(collection, user_id, rest_parameter, document_id, document_id_name):
	"""
	This method checks if the user_id has permission for the specific category, sub category etc 
	in a particular module 

	the permission can be of four types, create, get, delete , put
	create is the permission if a user can create child category of this partiular category
	Args:
		rest_parameter: "get", "put", "create", "delete"

	"""
	logger.info(type(document_id))
	docuemnt = yield collection.find_one({document_id_name: document_id}, \
									projection={"_id": False, document_id_name: True, user_id: True })
	if not document:
		raise Exception("The document with id[%s] doesnt exists"%(document_id)

	if not document.get(user_id, None):
		raise Exception("The document with id[%s] doest have permissions for user_id [%s]"%(document_id, user_id))

	try:
		if document[user_id][rest_parameter]:
			logger.info("The user_id [%s] has [%s] permissions for this document [%s]"%(user_id, rest_parameter, document_id))
			return True
	except Exception:
			logger.info("The user_id [%s] doesnt have [%s] permissions for this document [%s]"%(user_id, rest_parameter, document_id))
			return False

	return 



class LevelPermissions(tornado.web.RequestHandler):
	def initialize(self):
		self.db = self.settings["db"]
		self.category_collection = self.db[category_collection_name]	
		self.user_collection = self.db[user_collection_name]
		self.sub_category_collection = self.db[sub_category_collection_name]
		self.sub_criteria_collection = self.db[sub_criteria_collection_name]
		self.level_collection = self.db[level_collection_name]
		self.document_id_name = "level_id"

	@asynchronous
	@coroutine
	def post(self):
		"""
		permission_dict will have two keys
		so the categories collection will have a super_permissions entry in which there will be an "all" key
		which will have a list of all the user_ids who can do anything with this collection

		permission list will be a list of dict, with each dict is of the form
		[{"user_id": "user_id", "create": True, "edit": True, "delete": True, "update": True}, ]

		First check if category_id exists or not, 
	


		"""
		post_arguments = json.loads(self.request.body.decode("utf-8"))
		user_id = post_arguments.get("user_id", None)
		permissions = post_arguments.get("permissions", None)
		level_id = post_arguments.get("level_id", None)
		logger.info(post_arguments)
		try:
			assert isinstance(permissions, list), "permissions must be an array of objects"
			assert level_id is not None, "level_id cannot be left empty"
			assert user_id is  not None, "user_id cannot be left empty"

			##rest_paramter is "create", because only the admin who have create permission on this category 
			##will have the right to change admin for this particular category
			yield if_module_permission(self.level_collection, user_id, "create", level_id, self.document_id_name)
			
			logger.info("The user [%s] have create permission on level [%s]"%(user_id, level_id))

			for permission_obj in permissions:
					user_id = permission_obj.pop("user_id")
					update_level_collection = yield self.level_collection.update_one({"level_id": level_id}, \
						{"$set": {user_id: permission_obj}}, upsert=True)
					logger.info(update_level_collection.modified_count)

					update_user_collection = yield self.user_collection.update_one({"user_id": user_id}, \
						{"$set": {"permissions.level.%s"%level_id: permission_obj}}, upsert=False)
					logger.info(update_user_collection.modified_count)


		except Exception as e:
			logger.error(e)
			self.write({"error": True, "success": False, "message": e.__str__()})
			self.finish()
			return 
		self.write({"error": False, "success": True, "level_id": level_id, "message": "Permissions updated"})
		self.finish()
		return 







@auth
class Level(tornado.web.RequestHandler):
	def initialize(self):
		self.db = self.settings["db"]
		self.category_collection = self.db[category_collection_name]	
		self.user_collection = self.db[user_collection_name]
		self.sub_category_collection = self.db[sub_category_collection_name]
		self.sub_category_collection = self.db[sub_criteria_collection_name]
		self.level_collection = self.db[level_collection_name]
		self.document_id_name = "level_id"

	@asynchronous
	@coroutine
	##@categoryauth
	def post(self):
			"""
			Also module_type is sub_category
			"""
			#permissions = {"create": False, "delete": False, "edit": False, "get": False}
			post_arguments = json.loads(self.request.body.decode("utf-8"))
			level_name = post_arguments.get("level_name", None)
			text_description = post_arguments.get("text_description", None)
			score = post_arguments.get("text_description", None)
			user_id = post_arguments.get("user_id", None) ##who created this category
			sub_criteria_id = post_arguments.get("sub_criteria_id", None)

			
			try:
					##name of the parent category, subcategory. subcriteria etc
					sub_criteria = yield if_create_permissions(self.user_collection, \
						self.sub_criteria_collection, self.level_collection, user_id, "create", sub_criteria_id)


					level = yield self.level_collection.find_one({"level_name": level_name})

					if level:
						raise Exception("%s level already exists"%(level_name))

					level_hash = "%s%s"%(user_id, level_name)

					level_id = hashlib.sha1(level_hash.encode("utf-8")).hexdigest()
					

					sub_criteria["parents"].insert({"name": sub_criteria["sub_criteria_name"], "id": sub_criteria["sub_criteria_id"]})
					logger.info(sub_category["parents"])
					level = yield self.sub_category_collection.insert_one({"level_id": level_id, \
																			"level_name": level_name,
																			"module_type": "level",
																			"sub_criteria_name": sub_criteria["sub_criteria_name"],
																			"sub_criteria_id": sub_criteria["sub_criteria_id"],
																			"sub_category_id": sub_criteria["sub_category_id"],
																			"sub_category_name": sub_criteria["sub_category_name"],
																			"category_name": sub_criteria["category_name"],
																			"category_id": sub_criteria["category_id"],
																			"parents": sub_criteria["parents"], 
							"user_id": user_id, "score": score, "text_description": text_description, 
							"utc_epoch": time.time(), "indian_time": indian_time()})
					logger.info("New Level with name %s and _id=%s created by user id [%s]"%(level_name,\
					 level.inserted_id, user_id))


					permission = {"create": True, "delete": True, "update": True, "get": True}
					##this will add the creator id crud operation permission to this category

					update_sub_level_collection = yield self.level_collection.update_one({"level_id": level_id}, \
											{"$set": {user_id: permission}}, upsert=False)

					update_user_collection = yield self.user_collection.update_one({"user_id": user_id}, \
						{"$set": {"permissions.level.%s"%level_id: permission}}, upsert=False)


			except Exception as e:
				logger.error(e)
				self.write({"error": True, "success": False, "message": e.__str__()})
				self.finish()
				return 
			self.write({"error": False, "success": True, "level_id": level_id,  "sub_criteria_id": sub_criteria["sub_criteria_id"]})
			self.finish()
			return 
			


	@asynchronous
	@coroutine
	##allowed roles is user who has been assigned this category and admin
	def get(self, level_id):
			get_arguments = json.loads(self.request.body.decode("utf-8"))
			user_id = get_arguments.get("user_id", None) ##who created this category
			##Here we dont need parent category id, We just have to check the userid and its
			##get permission on the subcategory
			#user_permission = yield self.collection.find_one({"name": "super_permissions", "all": {"$in": [user_id]}}, projection={"_id": True})
			try:
				yield if_module_permission(self.sub_criteria_collection, user_id, "get", level_id, self.document_id_name)

				criteria = yield self.level_collection.find_one({"level_id": level_id}, projection={"_id": False, 
						"text_description": True, "score": True, "level_name": True})
			except Exception as e:
				print (traceback.format_exc())
				logger.error(e)
				self.write({"error": True, "success": False, "message": e.__str__()})
				self.finish()
				return 
			self.write({"error": False, "success": True, "level": level})
			self.finish()
			return 


	@asynchronous
	@coroutine
	def put(self, level_id):
			"""
			This will be used to change text desciption, overall score only by the superadmin, 
			and the user who created it, and the user who have been allowed to do so
			"""
			post_arguments = json.loads(self.request.body.decode("utf-8"))
			
			text_description = post_arguments.get("text_description", None)
			score = post_arguments.get("score", None)
			user_id = post_arguments.get("user_id", None) ##who created this category
			try:
				yield if_module_permission(self.level_collection, user_id, "put", level_id, self.document_id_name)

				self.level_collection.update_one({"level_id": level_id}, {"$set":{"text_description": text_description,\
						"score": score}}, upsert=False)					

			except Exception as e:
				print (traceback.format_exc())
				logger.error(e)
				self.write({"error": True, "success": False, "message": e.__str__()})
				self.finish()
				return 
			self.write({"error": False, "success": True, "level_id": level_id})
			self.finish()
			return 



	@asynchronous
	@coroutine
	def delete(self, level_id):
			"""
			Only the superadmin and the admin who created it will be able to delete this category
			And also the user who have been given persmissions to do so.
			"""
			post_arguments = json.loads(self.request.body.decode("utf-8"))
			user_id = post_arguments.get("user_id", None) ##who created this category
			try:
				yield if_module_permission(self.level_collection, user_id, "delete", level_id, self.document_id_name)
			except Exception as e:
				print (traceback.format_exc())
				logger.error(e)
				self.write({"error": True, "success": False, "message": e.__str__()})
				self.finish()
				return 
			self.write({"error": False, "success": True, "level_id": level_id})
			self.finish()
			return 



class SubCriterions(tornado.web.RequestHandler):
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
		self.category_collection = self.db[category_collection_name]	
		self.user_collection = self.db[user_collection_name]
		self.sub_category_collection = self.db[sub_category_collection_name]
		self.sub_criteria_collection = self.db[sub_criteria_collection_name]
		self.level_collection = self.db[level_collection_name]



	@asynchronous
	@coroutine
	def post(self):
		post_arguments = json.loads(self.request.body.decode("utf-8"))
		user_id = post_arguments.get("user_id", None) ##who created this category
		level_id = post_arguments.get("level_id", None)
		limit = post_arguments.get("limit", 10)
		skip = post_arguments.get("skip", 0)
		try:
			level = yield self.level_collection.find({"level_id": level_id, \
				"%s.%s"%(user_id, "get"): True}, projection={"_id": False}).\
					skip(skip).sort([('indian_time', -1)]).to_list(length=limit)
		except Exception as e:
			print (traceback.format_exc())
			logger.error(e)
			self.write({"error": True, "success": False, "message": e.__str__()})
			self.finish()
			return 
		self.write({"error": False, "success": True, "result": level})
		self.finish()
		return 















