



#!/usr/bin/env python3
from SettingsModule.settings import question_collection_name, default_document_limit,\
									indian_time, permissions, sub_category_collection_name,\
									category_collection_name

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
class SubCategory(tornado.web.RequestHandler):
	def initialize(self):
		self.db = self.settings["db"]
		self.parent_collection = self.db[category_collection_name]
		self.collection = self.db[sub_category_collection_name]	

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


			Steps to consider:
				1. A user must either have a superadmin on parent collection [category A]
				2. A user must be superadmin [ Category B]
				3. A user must have create permission on the parent category. [ category C]

				category A      
								subcategory AA
													level AAA
													level AAB
													level AAC
				

								subacategory AB

													level ABA
													level ABB
													level ABC

				category B 
								subcategory BA

													level BAA
													level BAB
													level BAC


				category C
								subcategory CA

				Make a superadmin list
				superadmin can do anything.
				admin can do anything with the systme created by the user, created by him 
				cases:
					category:

						superadmin: superadmin on category collection, can do anything
						
						admin 1: application level superadmin, can do anything, i.e admin
						admin 2: admin 2

						
						admin1_user_1: created by admin 1. 
						admin1_user_2: created by admin 2.

						admin1_user3:
						admin2_user4:

						admin1 will see admin1_user1, admin1_user2, so as admin2 its users and its categories, subcategories and levels


						Task A: admin 1: creates a Category A, permission can be granted to admin1 user by superadmin or admin. 
								permissions:
									admin1 provides admin1_user3 all permissions to this Category A, admin1_user3 can do anything 
									with this category and its children.
								
								POST:		/category/permissions/:id
								[{"user_id": , "create": True, "get": True, "put": True, "delete": True}]
								
								when clicked on provide permissions, the admin will click on this category, all
								the users made by this admin will appear.
								the admin will select multiple user and give them any permission, get, update, put, delete.

								make a post request with these permissions on POST above.

						Task B: admin 1: Creates Subcategory AA, and AB,  permission can be granted by admin1 or superadmin to anyone.
										provided they have at least have get on parent_id(True then only he can see it)
								POST:		/subcategory/permissions/:id
								[{"parent_id": [parent] , user_id": , "create": True, "get": True, "put": True, "delete": True}]
								check if user_id has create permission on parent id.
							


							SubTask B:
								admin 1 provides GET permission to admin1_user1 to this subcategory, 
								when clicks on subcategory ot provide permissions, four buttons will appear,
								

								when clicked to provide permissions, only the users created by this admin
								who will have get permission on this subcategory will be able to see it.

								same with any other put delete
								when clicked on provide permissions, All the users who have get request must be shown 
								as potential users to get permission
								
								if tries to provide create on this subcategory, it can provide, so it can create its subsubcategories
								if tries to delete, can provide
								if tries to update, can provide 



						Task C: admin 1 : Creates level AAA, AAB, AAC, permissions can be granted by admin1 to its users or by superadmin to anyone.
								POST:		/category/permissions/:id
								[{"parent_id": [superparent, parent] , user_id": , "create": True, "get": True, "put": True, "delete": True}]
								check if user_id has create permission on parent id.
					

						Task D: admin1_user3: Creates category:  only possible when admin1 makes admin1_user3 its admin, then rst
																	is same.

						Task E: admin1_user2: creates subcategory AD
								requirements: 
									first it must have get permission on Category A, so this user can see it
									while attempting, should look for create permission on category A, 
									if True:
											can create a subcategory AD


						Task F: admin1_user3: creates sub-sub-category AAC
								requirements: 
										least is, get on parent, get on sub category.
										first it must have permission on Category A, 
										then get on Sub category AA, then on sub sub category.




						Category Level Permissions: 
							GET: admin1 grants get permission to admin2 or any other user to category A, now can see all subcategories
								and levels.
							POST: admin1 grants post permission to admin2 or any other user to cat A, now can make new subcategories and levels.
							DELETE: can delete category and children
							update: can update anything.

						Sub Category Level Permissions:
							requirement: 
								user must have create and get permission on the parent category.



						Level based permissions:
							requirement:
								user must get on category, get and create on subcategory.

							
						

						admin2:


						Admin1: 









						admin1_user1: have permission on category A, all permissions, created by user admin1_user1
						admin1_user2: have permissions on category B, all permissions, created by user admin1_user2
						


						admin1: category: asigns permissions to all or any of its users to this category.

						admin1: subcategory: asigns permissions to all or any of its users to this subcategory.



						admin1_user1: creates new subcategory, visible only to admin1 not to admin1_user2
									parmissions can be given by either admin1 or superadmin.

									cant create subcategory at categoryB, unless provide permissions by admin2 or superamdin





						user 5: only have get permission on category A.
						user 6: have get, put but not delete permission on category A
						if user have create permission on any specific category, it automatically becomes the admin of that category.


						user 3 provided user 4, get permissions on category A. now he can see all subcategories of category A but
						cant do anything with them.

						
						superadmin provided all permission to user 4 on category A, he can do anything he wants.
						with category A, its subcategories and its levels. can also delete it

					subcategory:
						user 2 creates a subcategory, visible to all admins and superadmins but not to user 3 or 4.
						user 3 creates a subcategory, visible to him, admin and superadmins but not to user 4.

						superadmin provides permissions to user3 on category B(created by user 4).
						user 3 creates a subcategory, on the category created B
						handled: Now user 4 cant delete this sub category, unless provide permissions

						user 3 creates a subcategory created on category created by him.


						




					when superadmin, admin creates category, admin sees only the list of the user he created to provide
					permissions to them.
					superadmin sees all users.


					user 3 creates category, user 4 cannt delete, get or delete it unless provided permission by the user, admin or superadmin.

			





			"""
			#permissions = {"create": False, "delete": False, "edit": False, "get": False}
			post_arguments = json.loads(self.request.body.decode("utf-8"))
			category_name = post_arguments.get("category_name", None)
			text_description = post_arguments.get("text_description", None)
			score = post_arguments.get("text_description", None)
			user_id = post_arguments.get("user_id", None) ##who created this category
			user_permission = yield self.collection.find_one({"name": "super_permissions", "all": {"$in": [user_id]}}, projection={"_id": True})
			permissions = post_arguments.get("permissions", None)
			parent_category_id = post_arguments.get("parent_category_id", None)

			logger.info(post_arguments)
			try:
					# if not user_permission:
					# 	if user_id == "superadmin":
					# 		pass
					# 	else:
					# 		raise Exception("Insufficient permission for this user")

					##this checks whether the user have cretae permission on the parent category
					yield check_if_super(category_name, self.parent_collection, user_id, "post", None)

					category = yield self.collection.find_one({"category_name": category_name})
					if category:
						raise Exception("%s category already exists"%(category_name))

					category_hash = "%s%s"%(user_id, category_name)

					category_id = hashlib.sha1(category_hash.encode("utf-8")).hexdigest()
					category = yield self.collection.insert_one({"category_id": category_id, "category_name": category_name, 
							"user_id": user_id, "score": score, "text_description": text_description, "parent_category_id": parent_category_id})
					logger.info("New sub category with name %s and _id=%s created"%(category_name, category.inserted_id))

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












