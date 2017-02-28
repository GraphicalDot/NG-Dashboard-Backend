



#!/usr/bin/env python3
from SettingsModule.settings import question_collection_name, default_document_limit,\
									indian_time, permissions, category_collection_name,\
									app_super_admin, app_super_admin_pwd, app_super_admin_user_id,\
									user_collection_name, sub_category_collection_name, \
									indian_time

from AuthenticationModule.authentication import auth
from tornado.web import asynchronous
from tornado.gen import coroutine
import tornado
from LoggingModule.logging import logger
import hashlib
import json
import traceback

@coroutine
def check_if_super_sub_category(user_collection, category_collection, sub_category_collection, \
													user_id, rest_parameter, category_id):
	"""
	If a user want to create a SubCategory

	superadmin can create anything
	The user must have get and create permission on parent category

	when created the user will have all permissions on this sub category
	"""

	category = yield category_collection.find_one({"category_id": category_id}, \
		projection={"_id": False, user_id: True, "category_name": True})
	logger.info(category)
	logger.info(user_id)
	logger.info(category[user_id])
	logger.info(category[user_id][rest_parameter])				
	if not category:
			raise Exception("The category with categoryid=[%s] doesnt exists"%category_id)

	user = yield user_collection.find_one({"user_id": user_id}, projection={"_id": False, "user_type": True})
	logger.info(user)
	if not user:

			raise Exception("User doesnt exists")
	##Check if a user is superadmin
	if user["user_type"] == "superadmin":
			logger.info("User is among superadmin")
			return category["category_name"] 

	if not category[user_id]:
			raise Exception("The userid= [%s] doesnt have permissions to create subcategory on \
				category with categoryid=[%s]"%(user_id, category_id))



	##We dont have to check for get permissions has the userid cant see it, unless have
	##get permission on this subcategory
	if not category.get(user_id).get(rest_parameter, None):
			logger.info(category.get("user_id").get(rest_parameter, None))
			raise Exception("The userid= [%s] doesnt have %s permissions to on parent  \
				category with categoryid=[%s] doesnt exists"%(user_id, rest_parameter, category_id))

	return category["category_name"]
								   


@coroutine
def if_module_permission(sub_category_collection, user_id, rest_parameter, sub_category_id):
	"""
	This method checks if the user_id has permission for the specific category, sub category etc 
	in a particular module 

	the permission can be of four types, create, get, delete , put
	create is the permission if a user can create child category of this partiular category
	Args:
		rest_parameter: "get", "put", "create", "delete"

	"""
	logger.info(type(sub_category_id))
	sub_category = yield sub_category_collection.find_one({"sub_category_id": sub_category_id}, \
									projection={"_id": False, "sub_category_id": True, user_id: True })
	logger.info(sub_category)
	logger.info(sub_category_id)
	if not sub_category:
		raise Exception("The subcategory with id[%s] doesnt exists"%sub_category_id)

	if not sub_category.get(user_id, None):
		raise Exception("The subcategory with id[%s] doest have permissions for user_id [%s]"%(sub_category_id, user_id))

	try:
		if sub_category[user_id][rest_parameter]:
			logger.info("The user_id [%s] has [%s] permissions for this category [%s]"%(user_id, rest_parameter, sub_category_id))
			return True
	except Exception:
			logger.info("The user_id [%s] doesnt have [%s] permissions for this category [%s]"%(user_id, rest_parameter, sub_category_id))
			return False

	return 



class SubCategoryPermissions(tornado.web.RequestHandler):
	def initialize(self):
		self.db = self.settings["db"]
		self.category_collection = self.db[category_collection_name]	
		self.user_collection = self.db[user_collection_name]
		self.sub_category_collection = self.db[sub_category_collection_name]

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
		sub_category_id = post_arguments.get("sub_category_id", None)
		logger.info(post_arguments)
		try:
			assert isinstance(permissions, list), "permissions must be an array of objects"
			assert sub_category_id is not None, "sub_category_id cannot be left empty"
			assert user_id is  not None, "user_id cannot be left empty"

			##rest_paramter is "create", because only the admin who have create permission on this category 
			##will have the right to change admin for this particular category
			yield if_module_permission(self.sub_category_collection, user_id, "create", sub_category_id)
			
			logger.info("The user [%s] have create permission on sub_category [%s]"%(user_id, sub_category_id))

			for permission_obj in permissions:
					user_id = permission_obj.pop("user_id")
					update_category_collection = yield self.sub_category_collection.update_one({"sub_category_id": sub_category_id}, \
						{"$set": {user_id: permission_obj}}, upsert=True)
					logger.info(update_category_collection.modified_count)

					update_user_collection = yield self.user_collection.update_one({"user_id": user_id}, \
						{"$set": {"permissions.sub_category.%s"%sub_category_id: permission_obj}}, upsert=False)
					logger.info(update_user_collection.modified_count)


		except Exception as e:
			logger.error(e)
			self.write({"error": True, "success": False, "message": e.__str__()})
			self.finish()
			return 
		self.write({"error": False, "success": True, "sub_category_id": sub_category_id, "message": "Permissions updated"})
		self.finish()
		return 







@auth
class SubCategory(tornado.web.RequestHandler):
	def initialize(self):
		self.db = self.settings["db"]
		self.category_collection = self.db[category_collection_name]	
		self.user_collection = self.db[user_collection_name]
		self.sub_category_collection = self.db[sub_category_collection_name]

	@asynchronous
	@coroutine
	##@categoryauth
	def post(self):
			"""
			Also module_type is sub_category
			"""
			#permissions = {"create": False, "delete": False, "edit": False, "get": False}
			post_arguments = json.loads(self.request.body.decode("utf-8"))
			sub_category_name = post_arguments.get("sub_category_name", None)
			text_description = post_arguments.get("text_description", None)
			score = post_arguments.get("text_description", None)
			user_id = post_arguments.get("user_id", None) ##who created this category
			category_id = post_arguments.get("category_id", None)

			
			try:
					category_name = yield check_if_super_sub_category(self.user_collection, \
						self.category_collection, self.sub_category_collection, user_id, "create", category_id)


					sub_category = yield self.sub_category_collection.find_one({"category_name": sub_category_name})

					if sub_category:
						raise Exception("%s category already exists"%(category_name))

					sub_category_hash = "%s%s"%(user_id, sub_category_name)

					sub_category_id = hashlib.sha1(sub_category_hash.encode("utf-8")).hexdigest()
					category = yield self.sub_category_collection.insert_one({"sub_category_id": sub_category_id, \
																			"sub_category_name": sub_category_name,
																			"module_type": "sub_category",
																			"category_id": category_id,
																			"category_name": category_name,
							"user_id": user_id, "score": score, "text_description": text_description, 
							"utc_epoch": time.time(), "indian_time": indian_time()})
					logger.info("New sub category with name %s and _id=%s created by user id [%s]"%(sub_category_name,\
					 category.inserted_id, user_id))


					permission = {"create": True, "delete": True, "update": True, "get": True}
					##this will add the creator id crud operation permission to this category

					update_category_collection = yield self.sub_category_collection.update_one({"sub_category_id": sub_category_id}, \
											{"$set": {user_id: permission}}, upsert=False)

					update_user_collection = yield self.user_collection.update_one({"user_id": user_id}, \
						{"$set": {"permissions.sub_category.%s"%sub_category_id: permission}}, upsert=False)


			except Exception as e:
				logger.error(e)
				self.write({"error": True, "success": False, "message": e.__str__()})
				self.finish()
				return 
			self.write({"error": False, "success": True, "category_id": category_id,  "sub_category_id": sub_category_id})
			self.finish()
			return 
			


	@asynchronous
	@coroutine
	##allowed roles is user who has been assigned this category and admin
	def get(self, sub_category_id):
			get_arguments = json.loads(self.request.body.decode("utf-8"))
			user_id = get_arguments.get("user_id", None) ##who created this category
			##Here we dont need parent category id, We just have to check the userid and its
			##get permission on the subcategory
			#user_permission = yield self.collection.find_one({"name": "super_permissions", "all": {"$in": [user_id]}}, projection={"_id": True})
			try:
				logger.info("This is the sub category id %s"%sub_category_id)
				yield if_module_permission(self.sub_category_collection, user_id, "get", sub_category_id)

				category = yield self.sub_category_collection.find_one({"sub_category_id": sub_category_id}, projection={"_id": False, 
						"text_description": True, "score": True, "category_name": True})
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
			try:
					yield check_if_super_sub_category(self.user_collection, self.category_collection, self.sub_category_collection, \
													user_id, "create", category_id)
					yield check_if_super(None, self.user_collection, self.category_collection, user_id, "put", None)

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
			try:
				yield check_if_super_sub_category(self.user_collection, self.category_collection, self.sub_category_collection, \
													user_id, "create", category_id)
			except Exception as e:
				print (traceback.format_exc())
				logger.error(e)
				self.write({"error": True, "success": False, "message": e.__str__()})
				self.finish()
				return 
			self.write({"error": False, "success": True, "category_id": category_id})
			self.finish()
			return 



class SubCategories(tornado.web.RequestHandler):
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



	@asynchronous
	@coroutine
	def post(self):
		post_arguments = json.loads(self.request.body.decode("utf-8"))
		user_id = post_arguments.get("user_id", None) ##who created this category
		category_id = post_arguments.get("category_id", None)
		limit = post_arguments.get("limit", 10)
		skip = post_arguments.get("skip", 0)
		try:
			sub_categories = yield self.sub_category_collection.find({"category_id": category_id, \
				"%s.%s"%(user_id, "get"): True}, projection={"_id": False}).\
					skip(skip).sort([('indian_time', -1)]).to_list(length=limit)
		except Exception as e:
			print (traceback.format_exc())
			logger.error(e)
			self.write({"error": True, "success": False, "message": e.__str__()})
			self.finish()
			return 
		self.write({"error": False, "success": True, "result": sub_categories})
		self.finish()
		return 















