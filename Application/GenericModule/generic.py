
#!/usr/bin/env python3
from SettingsModule.settings import question_collection_name, default_document_limit,\
									indian_time, permissions, category_collection_name,\
									app_super_admin, app_super_admin_pwd, app_super_admin_user_id,\
									user_collection_name, criteria_collection_name, \
									indian_time, sub_criteria_collection_name, level_collection_name

from AuthenticationModule.authentication import auth
from tornado.web import asynchronous
from tornado.gen import coroutine
import tornado
from LoggingModule.logging import logger
import hashlib
import json
import traceback
import time 
import uuid


@coroutine
def if_create_permissions(user_collection, parent_collection, module_collection, \
						user_id, rest_parameter, parent_id, document_name,\
						parent_collection_name):
	"""
	If a user want to create a SubCategory

	superadmin can create anything
	The user must have get and create permission on parent category

	when created the user will have all permissions on this sub category
	"""
	user = yield user_collection.find_one({"user_id": user_id}, projection={"_id": False, "user_type": True})

	if not user:
			raise Exception("User doesnt exists")
	if parent_collection_name:
			parent = yield parent_collection.find_one({"module_id": parent_id})
	else:
		parent = None

	if not parent:
			## This implies that if parent document doestn exists, then two cases might happen
			## case 1 : the user is admin and wants to create a criteria  
			if user["user_type"] == "admin" and document_name == "criteria":
					logger.info("The user is [%s] and [%s] is being created"%(user["user_type"], "criteria"))
					return True
			##case 2: the user is superadmin and wants to create criteria, which doestn have 
			##any parent for it
			if user["user_type"] == "superadmin" and document_name == "criteria":
					logger.info("The user is [%s] and [%s] is being created"%(user["user_type"], "criteria"))
					return True

			raise Exception("The parent with id=[%s] doesnt exists"%parent_id)




	##Check if a user is superadmin
	if user["user_type"] == "superadmin":
			##returning whole parent document, which will be used to extract necessary information
			return parent 

	logger.info(parent)
	if not parent.get("user_permissions").get(user_id, None):
			raise Exception("The userid= [%s] doesnt have permissions to create children on \
				parent with parent_id=[%s]"%(user_id, parent_id))



	##We dont have to check for get permissions has the userid cant see it, unless have
	##get permission on this subcategory
	if not parent.get("user_permissions").get(user_id).get(rest_parameter, None):
			raise Exception("The userid= [%s] doesnt have %s permissions to on parent  \
				with parent id=[%s] doesnt exists"%(user_id, rest_parameter, parent_id))

	return parent
								   


@coroutine
def if_module_permission(collection, user_id, rest_parameter, module_id):
	"""
	This method checks if the user_id has permission for the specific category, sub category etc 
	in a particular module 

	the permission can be of four types, create, get, delete , put
	create is the permission if a user can create child category of this partiular category
	Args:
		rest_parameter: "get", "put", "create", "delete"

	"""
	document = yield collection.find_one({"module_id": module_id}, \
									projection={"_id": False, "user_permissions": True, "module_id": True})
	if not document:
		raise Exception("The document with id[%s] doesnt exists"%(module_id))

	if not document["user_permissions"].get(user_id, None):
		raise Exception("The document with id[%s] doest have permissions for user_id [%s]"%(module_id, user_id))

	try:
		if document["user_permissions"][user_id][rest_parameter]:
			logger.info("The user_id [%s] has [%s] permissions for this document [%s]"%(user_id, rest_parameter, module_id))
			return True
	except Exception:
			logger.info("The user_id [%s] doesnt have [%s] permissions for this document [%s]"%(user_id, rest_parameter, module_id))
			return False

	return 


@coroutine
def delete_children(db, children, child_collection_name):
	logger.info(child_collection_name)
	logger.info(children)
	collection = db[child_collection_name]
	for child in children:
		child = yield collection.find_one({"module_id": child["module_id"]})
		logger.info(child["module_id"])
		logger.info(child)
		delete_id = yield collection.delete_one({"module_id": child["module_id"]})
		try:
			child_children = child["children"]
			child_child_collection_name = child["child_collection_name"]
			logger.info(child["module_type"])
			logger.info(child_children)
			logger.info(child_child_collection_name)
			logger.info("\n")
			if child_child_collection_name:
				delete_children(db, child_children, child_child_collection_name)
		except Exception as e:
			logger.info(e)
			pass

	return False



class GenericPermissions(tornado.web.RequestHandler):
	def initialize(self):
		self.db = self.settings["db"]
		self.user_collection = self.db[user_collection_name]
		self.parent_collection = self.db[sub_criteria_collection_name]
		self.module_collection = self.db[level_collection_name]
		self.document_id = "level_id"
		self.document_name = "level"

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
		module_id = post_arguments.get("module_id", None)
		logger.info(post_arguments)
		try:
			assert isinstance(permissions, list), "permissions must be an array of objects"
			assert module_id is not None, "module_id  cannot be left empty"
			assert user_id is  not None, "user_id cannot be left empty"

			##rest_paramter is "create", because only the admin who have create permission on this category 
			##will have the right to change admin for this particular category
			yield if_module_permission(self.module_collection, user_id, "create", module_id)
			
			logger.info("The user [%s] have create permission on %s [%s]"%(user_id, self.document_id, module_id))
			yield self.module_collection.update_one({"module_id": module_id},  
					{"$addToSet": {"history.change_paermissions": {"user_id": user_id, "utc_epoch": time.time(), 
					"indian_time": indian_time(), "action": permissions}}}, upsert=False)

			for permission_obj in permissions:
					user_id = permission_obj.pop("user_id")
					update_module_collection = yield self.module_collection.update_one({"module_id": module_id}, \
						{"$set": {"user_permissions.%s"%user_id: permission_obj}}, upsert=True)
					logger.info(update_module_collection.modified_count)

					update_user_collection = yield self.user_collection.update_one({"user_id": user_id}, \
						{"$set": {"permissions.%s.%s"%(self.document_name, module_id): permission_obj}}, upsert=False)
					logger.info(update_user_collection.modified_count)


		except Exception as e:
			print (traceback.format_exc())
			logger.error(e)
			self.write({"error": True, "success": False, "message": e.__str__()})
			self.finish()
			return 
		self.write({"error": False, "success": True, "module_id": module_id, \
						"message": "Permissions updated for %s with id=[%s]"%("module_id", module_id)})
		self.finish()
		return 







class Generic(tornado.web.RequestHandler):
	def initialize(self):
		self.db = None
		self.user_collection = None
		self.parent_collection_name = None
		self.parent_collection = None
		self.module_collection = None
		self.document_id = "sub_category_id"
		self.document_name = "sub_category"
		self.child_collection = None
		self.child_collection_name = None



	@asynchronous
	@coroutine
	##@categoryauth
	def post(self):

			"""Also module_type is sub_category
			"""
			#permissions = {"create": False, "delete": False, "edit": False, "get": False}
			post_arguments = json.loads(self.request.body.decode("utf-8"))

			##example is document_name is level, criteria, sub_criteria, question
			##that will also happen to be module_type when inserting the document
			## when getting the post arguments, _name will be appended to it
			## for example module_name will get level_name, criteria_name etc from the 
			##post arguments.
			module_name = post_arguments.get("%s_name"%self.document_name, None)
			text_description = post_arguments.get("text_description", None)
			score = post_arguments.get("score", None)
			user_id = post_arguments.get("user_id", None) ##who created this category
			parent_id = post_arguments.get("parent_id", None)
			try:
					if self.document_name == "question":
						documents_required = post_arguments.get("documents_required")
						assert isinstance(documents_required, list), "documents_required cannot be left empty"
					

					assert module_name is not None, "module_name  cannot be left empty"
					assert user_id is  not None, "user_id cannot be left empty"


					##name of the parent category, subcategory. subcriteria etc
					parent_document = yield if_create_permissions(self.user_collection, \
						self.parent_collection, self.module_collection, user_id, "create", parent_id, self.document_name, self.parent_collection_name)


					module_document = yield self.module_collection.find_one({"%s_name"%self.document_name: module_name})

					if module_document:
						raise Exception("%s on %s module already exists"%(module_name, self.document_name))

					module_hash = "%s%s"%(user_id, module_name)

					module_id = hashlib.sha1(module_hash.encode("utf-8")).hexdigest()
					
					##this implies that an admin or superadmin wants to create a criteria(parent module) for 
					##this application, because this parent will not have any parent_collection_name
					if self.parent_collection_name:
							parent_document["parents"].append({"name": parent_document["module_name"], "id": parent_document["module_id"],
																"module_type": parent_document["module_type"] })
							parents = parent_document["parents"]
							##This will add a children to the parent collection
							self.parent_collection.update({"module_id": parent_id}, {"$addToSet": \
								{"children": {"module_id": module_id, "module_name": module_name, "module_type": self.document_name}}}, upsert=False)

					else:
							parents = []

					data = {"module_id": module_id, "module_name": module_name, "module_type": self.document_name,\
							"parent_id": parent_id, "parents": parents, \
							"child_collection_name": self.child_collection_name, "user_id": user_id,\
							 "score": score, "text_description": text_description, "utc_epoch": time.time(), \
							 "indian_time": indian_time(), "children": [], "parent_collection_name": self.parent_collection_name}

					result = yield self.module_collection.insert_one(data)

					permission = {"create": True, "delete": True, "update": True, "get": True}
					##this will add the creator id crud operation permission to this category

					update_module_collection = yield self.module_collection.update_one({"module_id": module_id}, \
											{"$set": {"user_permissions.%s"%user_id: permission}}, upsert=False)

					update_user_collection = yield self.user_collection.update_one({"user_id": user_id}, \
						{"$set": {"permissions.%s.%s"%(self.document_name, module_id): permission}}, upsert=False)


			except Exception as e:
				print (traceback.format_exc())
				logger.error(e)
				self.write({"error": True, "success": False, "message": e.__str__()})
				self.finish()
				return 
			self.write({"error": False, "success": True, "message": None, "module_id": module_id, \
								 "parent_id": parent_id})
			self.finish()
			return 
			


	@asynchronous
	@coroutine
	##allowed roles is user who has been assigned this category and admin
	def get(self, module_id):
			get_arguments = json.loads(self.request.body.decode("utf-8"))
			user_id = get_arguments.get("user_id", None) ##who created this category
			##Here we dont need parent category id, We just have to check the userid and its
			##get permission on the subcategory
			#user_permission = yield self.collection.find_one({"name": "super_permissions", "all": {"$in": [user_id]}}, projection={"_id": True})
			try:
				yield if_module_permission(self.module_collection, user_id, "get", module_id)

				result = yield self.module_collection.find_one({"module_id": module_id}, projection={"_id": False, 
						"text_description": True, "score": True, self.document_name: True})

				yield self.module_collection.update_one({"module_id": module_id},  
					{"$addToSet": {"history.get": {"user_id": user_id, "utc_epoch": time.time(), "indian_time": indian_time()}}}, upsert=False)


			except Exception as e:
				print (traceback.format_exc())
				logger.error(e)
				self.write({"error": True, "success": False, "message": e.__str__()})
				self.finish()
				return 
			self.write({"error": False, "success": True, "result": result, "message": None})
			self.finish()
			return 


	@asynchronous
	@coroutine
	def put(self, module_id):
			"""
			This will be used to change text desciption, overall score only by the superadmin, 
			and the user who created it, and the user who have been allowed to do so
			"""
			post_arguments = json.loads(self.request.body.decode("utf-8"))
			
			text_description = post_arguments.get("text_description", None)
			score = post_arguments.get("score", None)
			user_id = post_arguments.get("user_id", None) ##who created this category
			try:
				yield if_module_permission(self.module_collection, user_id, "put", module_id)

				self.module_collection.update_one({"module_id": module_id}, {"$set":{"text_description": text_description,\
					"score": score}}, upsert=False)					
				
				yield self.module_collection.update_one({"module_id": module_id},  
					{"$addToSet": {"history.put": {"user_id": user_id, "utc_epoch": time.time(), "indian_time": indian_time()}, 
							"action": post_arguments}}, upsert=False)				


			except Exception as e:
				print (traceback.format_exc())
				logger.error(e)
				self.write({"error": True, "success": False, "message": e.__str__()})
				self.finish()
				return 
			self.write({"error": False, "success": True, "message": None, "module_id": module_id})
			self.finish()
			return 



	@asynchronous
	@coroutine
	def delete(self, module_id):
			post_arguments = json.loads(self.request.body.decode("utf-8"))
			user_id = post_arguments.get("user_id", None) ##who created this category
			try:
				permissions = yield if_module_permission(self.module_collection, user_id, "delete", module_id)
				module = yield self.module_collection.find_one({"module_id": module_id})
				module_name = module["module_name"]

				children = module["children"]
				child_collection_name = module["child_collection_name"]
				
				yield self.module_collection.delete_one({"module_id": module_id})
				yield self.module_collection.update_one({"module_id": module_id},  
					{"$addToSet": {"history.delete": {"user_id": user_id, "utc_epoch": time.time(), "indian_time": indian_time()}}}, upsert=False)				

				##This dleetes the module id from the children field on the parent
				if module["parent_id"]:
					yield self.db[self.parent_collection_name].update({"module_id": module["parent_id"]},\
						{"$pull": {"children": {"module_id": module_id, "module_name": module_name}}})


				if child_collection_name:
					yield delete_children(self.db, children, child_collection_name)


				##TODO, Delete this category and all its children and children

			except KeyError as e:
				##implies that this one has no children
				self.write({"error": False, "success": True, "message": "module_id [%s] deleted"%module_id})
				self.finish()
				return 
			except Exception as e:
				print (traceback.format_exc())
				logger.error(e)
				self.write({"error": True, "success": False, "message": e.__str__()})
				self.finish()
				return 
			self.write({"error": False, "success": True, "module_id": module_id})
			self.finish()
			return 



class Generics(tornado.web.RequestHandler):

	def initialize(self):
		self.db = None
		self.user_collection = None
		self.module_collection = None
		self.document_id = "level_id"
		self.document_name = "level"



	@asynchronous
	@coroutine
	def post(self):
		post_arguments = json.loads(self.request.body.decode("utf-8"))
		user_id = post_arguments.get("user_id", None) ##who created this category
		limit = post_arguments.get("limit", 10)
		skip = post_arguments.get("skip", 0)
		parent_id = post_arguments.get("parent_id", None)
		"""
		Arguments:
			SO for an example application wants to get all the subcriteria on which user
			have required permissions.But if only user_id is provided the application will get
			all the subcriteria belonging to different criteria.

			What if application wants to get sucriteria belonging to a specific criteria  and with
			the user permissions available on these subcriteira.
			user_id:

			parent_id:
		"""
		try:
			result = yield self.module_collection.find({"parent_id": parent_id, "user_permissions.%s.%s"%(user_id, "get"): True}, \
				projection={"_id": False, "user_permissions": False}).\
			skip(skip).sort([('indian_time', -1)]).to_list(length=limit)
		except Exception as e:
			print (traceback.format_exc())
			logger.error(e)
			self.write({"error": True, "success": False, "message": e.__str__()})
			self.finish()
			return 
		self.write({"error": False, "success": True, "result": result})
		self.finish()
		return 














