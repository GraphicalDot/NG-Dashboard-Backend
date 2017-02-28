



#!/usr/bin/env python3
from SettingsModule.settings import question_collection_name, default_document_limit,\
									indian_time, permissions, category_collection_name,\
									app_super_admin, app_super_admin_pwd, app_super_admin_user_id,\
									user_collection_name

from AuthenticationModule.authentication import auth
from tornado.web import asynchronous
from tornado.gen import coroutine
import tornado
from LoggingModule.logging import logger
import hashlib
import json
import traceback

@coroutine
def check_if_super(category_name, user_collection, category_collection, user_id, rest_parameter, category_id=None):
	"""
	check if a user have the super user permission in the collection for the specifid category
	i.e his/her user_id is present in the "super_permissions", 
	if True: 
			Then this user_id can create more entries into this collection or any children of this category, 
	this method also checks if this user is superadmin for this application, 
	if True:
		he/she can do anything with this collection
	"""
	user = yield user_collection.find_one({"user_id": user_id}, projection={"_id": False, "user_type": True})
	if not user:
			raise Exception("User doesnt exists")


	if rest_parameter == "post":
		##which imlies that any superadmin or admin can create a category
		if user["user_type"] == "superadmin" or user["user_type"] == "admin":
			logger.info("User is among superadmin or admin ")
			return True 
	else:
		if user["user_type"] == "superadmin":
			logger.info("User is among superadmin")
			return True 


	permission = yield if_module_permission(category_name, category_collection, user_id, rest_parameter, category_id)
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



class CategoryPermissions(tornado.web.RequestHandler):
	def initialize(self):
		self.db = self.settings["db"]
		self.category_collection = self.db[category_collection_name]	
		self.user_collection = self.db[user_collection_name]

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
		category_id = post_arguments.get("category_id", None)
		try:
			assert isinstance(permissions, list), "permissions must be an array of objects"
			assert category_id is not None, "category_id cannot be left empty"
			assert user_id is  not None, "user_id cannot be left empty"

			##rest_paramter is "create", because only the admin who have create permission on this category 
			##will have the right to change admin for this particular category
			yield check_if_super(None, self.user_collection, self.category_collection, user_id, "create", category_id)
			logger.info("The user [%s] have create permission on category [%s]"%(user_id, category_id))

			for permission_obj in permissions:
					user_id = permission_obj.pop("user_id")
					update_category_collection = yield self.category_collection.update_one({"category_id": category_id}, \
						{"$set": {user_id: permission_obj}}, upsert=True)
					logger.info(update_category_collection.modified_count)

					update_user_collection = yield self.user_collection.update_one({"user_id": user_id}, \
						{"$set": {"permissions.category.%s"%category_id: permission_obj}}, upsert=False)
					logger.info(update_user_collection.modified_count)


		except Exception as e:
			logger.error(e)
			self.write({"error": True, "success": False, "message": e.__str__()})
			self.finish()
			return 
		self.write({"error": False, "success": True, "category_id": category_id, "messege": "Permissions updated"})
		self.finish()
		return 








@auth
class Category(tornado.web.RequestHandler):
	def initialize(self):
		self.db = self.settings["db"]
		self.category_collection = self.db[category_collection_name]	
		self.user_collection = self.db[user_collection_name]

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

			Steps to consider:
				1. A user must either have a superadmin on parent collection
				2. A user must be superadmin
-				3. A user either must have a get or create permission on the parent category.			
-
-				A user who created this subcategory automatically becomes its admin, get all permissions on 
-				this particular category.
-			#TODO: check if a user has create permission for this category, which implies that this user_id
-					has create permission for its parent_id
+				1. A user must either have a superadmin on parent collection [category A]
+				2. A user must be superadmin [ Category B]
+				3. A user must have create permission on the parent category. [ category C]
+
+				category A      
+								subcategory AA
+													level AAA
+													level AAB
+													level AAC
+				
+
+								subacategory AB
+
+													level ABA
+													level ABB
+													level ABC
+
+				category B 
+								subcategory BA
+
+													level BAA
+													level BAB
+													level BAC
+
+
+				category C
+								subcategory CA
+
+				Make a superadmin list
+				superadmin can do anything.
+				admin can do anything with the systme created by the user, created by him 
+				cases:
+					category:
+
+						superadmin: superadmin on category collection, can do anything
+						
+						admin 1: application level superadmin, can do anything, i.e admin
+						admin 2: admin 2
+
+						admin1_user_1: created by admin 1. 
+						admin1_user_2: created by admin 2.
+
+						admin1_user1:
+						admin2_user2:
+
+						admin1 will see admin1_user1, admin1_user2, so as admin2 its users and its categories, subcategories and levels
+
+
+						admin 1: creates a Category A, 
+
+						admin 1: Creates Subcategory AA, and AB, 
+
+						Admin1: 
+
+
+
+
+
+
+
+
+
+						admin1_user1: have permission on category A, all permissions, created by user admin1_user1
+						admin1_user2: have permissions on category B, all permissions, created by user admin1_user2
+						
+
+
+						admin1: category: asigns permissions to all or any of its users to this category.
+
+						admin1: subcategory: asigns permissions to all or any of its users to this subcategory.
+
+
+
+						admin1_user1: creates new subcategory, visible only to admin1 not to admin1_user2
+									parmissions can be given by either admin1 or superadmin.
+
+									cant create subcategory at categoryB, unless provide permissions by admin2 or superamdin
+
+
+
+
+
+						user 5: only have get permission on category A.
+						user 6: have get, put but not delete permission on category A
+						if user have create permission on any specific category, it automatically becomes the admin of that category.
+
+
+						user 3 provided user 4, get permissions on category A. now he can see all subcategories of category A but
+						cant do anything with them.
+
+						
+						superadmin provided all permission to user 4 on category A, he can do anything he wants.
+						with category A, its subcategories and its levels. can also delete it
+
+					subcategory:
+						user 2 creates a subcategory, visible to all admins and superadmins but not to user 3 or 4.
+						user 3 creates a subcategory, visible to him, admin and superadmins but not to user 4.
+
+						superadmin provides permissions to user3 on category B(created by user 4).
+						user 3 creates a subcategory, on the category created B
+						handled: Now user 4 cant delete this sub category, unless provide permissions
+
+						user 3 creates a subcategory created on category created by him.
+
+
+						
+
+
+
+
+					when superadmin, admin creates category, admin sees only the list of the user he created to provide
+					permissions to them.
+					superadmin sees all users.
+
+
+					user 3 creates category, user 4 cannt delete, get or delete it unless provided permission by the user, admin or superadmin.
+
+			

			"""
			#permissions = {"create": False, "delete": False, "edit": False, "get": False}
			post_arguments = json.loads(self.request.body.decode("utf-8"))
			category_name = post_arguments.get("category_name", None)
			text_description = post_arguments.get("text_description", None)
			score = post_arguments.get("text_description", None)
			user_id = post_arguments.get("user_id", None) ##who created this category
			try:
					yield check_if_super(category_name, self.user_collection, self.category_collection, user_id, "post", None)

					category = yield self.category_collection.find_one({"category_name": category_name})
					if category:
						raise Exception("%s category already exists"%(category_name))

					category_hash = "%s%s"%(user_id, category_name)

					category_id = hashlib.sha1(category_hash.encode("utf-8")).hexdigest()
					category = yield self.category_collection.insert_one({"category_id": category_id, "category_name": category_name, 
							"user_id": user_id, "score": score, "text_description": text_description})
					logger.info("New category with name %s and _id=%s created by user id [%s]"%(category_name, category.inserted_id, user_id))


					permission = {"create": True, "delete": True, "update": True, "get": True}
					##this will add the creator id crud operation permission to this category

					update_category_collection = yield self.category_collection.update_one({"category_id": category_id}, \
											{"$set": {user_id: permission}}, upsert=True)

					update_user_collection = yield self.user_collection.update_one({"user_id": user_id}, \
						{"$set": {"permissions.category.%s"%category_id: permission}}, upsert=False)


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
				yield check_if_super(None, self.user_collection, self.category_collection, user_id, "get", None)
				category = yield self.category_collection.find_one({"category_id": category_id}, projection={"_id": False})
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
				yield check_if_super(None, self.user_collection, self.category_collection, user_id, "delete", None)				
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













