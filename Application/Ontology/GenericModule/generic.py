import tornado.options
import tornado.web
from tornado.escape import json_decode as TornadoJsonDecode
from SettingsModule.settings  import domain_collection_name, indian_time, jwt_secret, \
									 default_document_limit, user_collection_name, permission_collection_name, \
									 action_collection_name

from .delete_module import DeleteModule
from .permissions import Permissions
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
import uuid
from GeneralModule.cors import cors
from pprint import pprint
reader = codecs.getreader("utf-8")

"""
admin will have all the get and add permissions pn all the objects.

If a user creates a module then he/she will have automatically the permissions 
to create its children. He will also have the get and edit permissions on this object.
Now   

In Get requests, Onlythose modules will  be rendered which will have creation_approval=True and
deletion_approval=False for users and admin users.
Superadmin will get all the modules.

"""
class GenericPermissions(tornado.web.RequestHandler):

	def initialize(self):
		self.db = self.settings["db"]
		self.parent_collection = None
		self.parent_name = None
		self.module_collection = None
		self.user_collection = None
		self.module_type = None
		self.child_collection = None
		self.child_collection_name = None
		self.permission_collection = db[permission_collection_name]
		self.action_collection = db[action_collection_name]
		
	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def get(self, module_id=None):

		pprint ("I received the get request")
		try:
			user_id = self.request.arguments.get("user_id")[0].decode("utf-8")
		except Exception : 
			user_id = None
		
		modules = []
		try:
			skip = self.request.arguments.get("skip")[0].decode("utf-8")
			limit = self.request.arguments.get("limit")[0].decode("utf-8")
		except Exception:
			skip = 0
			limit = 15
		user = yield self.user_collection.find_one({"user_id": user_id})
		
		if module_id:
			module = yield self.module_collection.find_one({"module_id": module_id})
			result = yield Permissions.get_permissions_modules(skip, limit, module, self.permission_collection, self.user_collection)
		else:
			result= yield Permissions.get_permissions_user(skip, limit, user, self.module_type, self.module_collection, self.permission_collection)
		
		
		pprint (result)
		self.write({"error": False, "success": True, "data": result})
		self.finish()
		return 






class Generic(tornado.web.RequestHandler):


	def initialize(self):
		self.db = self.settings["db"]
		self.parent_collection = None
		self.parent_name = None
		self.module_collection = None
		self.user_collection = None
		self.module_type = None
		self.child_collection = None
		self.child_collection_name = None
		self.permission_collection = db[permission_collection_name]
		self.action_collection = db[action_collection_name]
		


	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def options(self, domain_id=None, user_id=None):
        # no body
		self.set_status(204)
		self.finish()



	@tornado.gen.coroutine
	def add_children(self, parent_id, module_id, module_name):
		## Deletion approval is False when creation and will be True when a user submits its deletion
		## it will be deleted by admin when he would nod yes, If he says no, then its deletion will again be
		## False and cannot be deleted by this particular user.

		parent_document = yield self.parent_collection.find_one({"module_id": parent_id})
		if not parent_document:
			raise Exception("The parent id with id %s doesnt exists"%parent_id)
		if not parent_document["creation_approval"] or parent_document["deletion_approval"]:
			raise Exception("Parent module creation first shall be approved by superadmin or its deletion is pending")

		parent_document["parents"].append({"module_id": parent_id,
								"module_name": parent_document["module_name"] })
		parents = parent_document["parents"]
					##This will add a children to the parent collection
		yield self.parent_collection.update({"module_id": parent_id}, {"$addToSet": \
			{"children": {"module_id": module_id, "module_name": module_name}}}, upsert=False)

		return parents


	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def  post(self):
		if not self.request.body:
			raise Exception("Dude! I need some data")
		post_arguments = json.loads(self.request.body.decode("utf-8"))
		module_name = post_arguments.get("module_name", None)
		description = post_arguments.get("description", None)
		user_id = post_arguments.get("user_id")
		parent_id  = post_arguments.get("parent_id")
		
        ##Permissions
		##For the user other 
		
		#user = yield db[credentials].find_one({'user_type': user_type, "username": username, "password": password})
		
		pprint ("This is the parent id %s"%parent_id)
		try:
			if None in [module_name, description, user_id]:
				raise Exception("Fields shouldnt be empty")

			user = yield self.user_collection.find_one({"user_id": user_id})
			if not user:
				raise Exception("The user who is trying to create this domain doesnt exists")
				
			module = yield self.module_collection.find_one({"module_name": module_name, "description": description})
			if module:
				raise Exception("This module have already been created")


			##if module type is domain then user either must be superadmin, admin or must have create_domain  permissions on the parent, 
			## If a mosule type is not domain then the user must be check for admin superadmin or add child permissions.
			## The user can only add child if its creation approval is done by superadmin or get request must give 
			## only the modules which are creation approed or deletion approved false.
			is_domain = yield Permissions.is_domain(self.module_type, user)
			if not is_domain: ##this implies that other type of module is being created
				parent_module = yield self.parent_collection.find_one({"module_id": parent_id})
				
				child_in_parent = yield self.module_collection.find_one({"module_name": module_name, "parent_id": parent_id})
				if child_in_parent:
					raise Exception("child module with name %s has already been added to this module"%module_name)
				yield Permissions.is_not_domain(user, parent_module, self.module_type, self.permission_collection)
				
			##check if email is already registered with us

			_id = str(uuid.uuid4())
			
			module_id = "%s-%s"%(self.module_type, _id)
			logger.info(module_id)

			## This can be removed later on, i.e same name mustnot exists under same parent.


			if self.parent_collection:
				parents = yield self.add_children(parent_id, module_id, module_name)
			
			else:
				parents = []

			pprint (parents)
			##As this module is created by superadmin, it will not need any creation_approval approval
			if user["user_type"] == "superadmin":
				creation_approval = True
			else: 
				creation_approval = False
				

			#TODO
			module = {'module_name': "%s-%s"%(self.module_type, module_name), "description": description, "parent_id": parent_id, "parents": parents,
							 "module_id": module_id, "utc_epoch": time.time(), "indian_time": indian_time(), "username": user["username"],
							 "user_id": user_id, "status": True, "deletion_approval": False, "creation_approval": creation_approval, 
							  "module_type": self.module_type, "user_type": user["user_type"], "child_collection_name": self.child_collection_name, "children": []}
			
			
			
			yield self.module_collection.insert_one(module)

			## This statement will help in get object as user can only get documents on which he has permission
			##or which he created, he will also have the add_child permission on this module too.
			if user["user_type"] != "superadmin" and user["user_type"] != "admin":
					yield Permissions.set_permission_from_obj(user, module, {"get": True, "edit": True, "add_child": True, "delete": False}, parent_id, 
					user["user_id"], self.permission_collection)

			logger.info("%s created at %s with module_id %s"%(self.module_type, indian_time(), module_id))
			#TODO: will be used to send email to the user
			##executor.submit(task, datetime.datetime.now())
		except Exception as e:
				logger.error(e)
				self.set_status(400)
				self.write({"error": True, "success": False, "token": None, "data": e.__str__()})
				self.finish()
				return 

		##This line has to be added, somehow while inserting nanoskill into the mongo, nanoskill itself got a new _id key
		##which is not serializable
		##TODO : implement JWT tokens
		module.pop("_id")
		self.write({"error": False, "success": True, "data": module})
		self.finish()
		return 




	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def put(self, module_id):
		##TODO if a user has to become a superadmin
		pprint (module_id)
		put_arguments = json.loads(self.request.body.decode("utf-8"))
		pprint (put_arguments)

		user_id = put_arguments.get("user_id") ##User to whom the permissions will be provided
		granter_id = put_arguments.get("granter_id") ##who is changing the permissions of this module
		permission = put_arguments.get("permission", None)
		creation_approval = put_arguments.get("creation_approval", None)
		module_data = put_arguments.get("module_data", None)

		pprint (put_arguments)
		try:
			__message = None
			module = yield self.module_collection.find_one({"module_id": module_id})
			parent_id = module["parent_id"]
			if not parent_id:
				parent_id = None
				parent = None
			else: 
				parent = yield self.parent_collection.find_one({"module_id": parent_id})


			granter = yield self.user_collection.find_one({"user_id": granter_id})
			user = yield self.user_collection.find_one({"user_id": user_id})
			if not user:
				raise Exception("This user doesnt exists")


			##actual deletion will be handled in delete request, which will delete the module and its children
			if module["deletion_approval"]:
				if user["uer_type"] == "superadmin":
					raise Exception("Deletion is pending for this module by superadmin")


			if creation_approval == "delete":
				if user["user_type"] == "superadmin":
							yield self.module_collection.delete({"module_id": module_id})
							yield self.permission_collection.delete_many({"module_id": module_id})
				else:
					raise Exception("Only superadmin can change creation approval status")			

			if creation_approval == True:
				## NO need to delete this domain_id from the permission because there will not be any entry for this domain_id
				##in the permission collection, as Get rest call will only return those domains which are creation approved. 
				if user["user_type"] == "superadmin":
							yield self.module_collection.update_one({"module_id": module_id}, {"$set": {"creation_approval": True}}, upsert=False)
				else:
					raise Exception("Only superadmin can change creation approval status")			

			if permission:
				assert isinstance(permission, dict), 'permissions shall of dict  type!'
				assert user_id != None
				assert granter_id != None
				#assert permission["get"], "Permission object has not get parameter" 
				#assert permission["edit"], "Permission object has not edit parameter"
				#assert permission["delete"], "Permission object has not delete parameter"
				##we only have to check for non superadmina nd admin user because they can do anything with any module
				__message = []
				if granter["user_type"] == "superadmin":

								pprint ("Adding permission by superadmin")
								yield Permissions.set_permission_from_obj(user, module, permission, parent_id, 
									granter_id, self.permission_collection)
				##is granter is superadmin or admin, all permissions will be added to the user
				else:
					pprint ("Adding permission by user_type who is not superadmin")
					for rest_parameter in ["get", "delete", "edit", "add_child"]:
						if permission[rest_parameter]:
							result = yield Permissions.get_permission_rest_parameter(granter, module, rest_parameter, self.permission_collection)
							if not result:
								raise Exception("Insufficient permissions to provide %s permission"%rest_parameter)
							else:
								print ("user_type <<%s>> with user_id<<%s>> have %s on %s"%(granter["user_type"], granter["user_id"], rest_parameter, module["module_id"]))
								yield Permissions.set_permission_rest_paramter(user, module, parent, granter, rest_parameter, self.permission_collection)





			if module_data:
				assert isinstance(module_data, dict), 'module_data shall of dict  type!'
				##we only have to check for non superadmina nd admin user because they can do anything with any module
				if not user["user_type"]:
					result = yield self.permission_collection.find({"user_id": granter_id, "module_id": module_id, "edit": True, 
							"module_type": self.module_type , "deletion_approval": False, 
						"creation_approval": True}, projection={"_id": False}).to_list(100)
					if not result:
						raise Exception("Insufficient permissions to add permissions")
			
				yield self.module_collection.update_one({"module_id": module_id}, {"$set": module_data}, upsert=False)	



		except Exception as e:
				logger.error(e)
				self.set_status(400)
				self.write({"error": True, "success": False, "token": None, "data": e.__str__()})
				self.finish()
				return 
	

		"""
		result = yield delete_edit_permissions(request_type="edit", user_id=user_id, 
                    collection_permissions=self.collcetion_permissions, 
                    user_collection=self.user_collection, 
                    object_id=object_id)
        
		if not result:
				domain = yield self.collection.find_one({"domain_id": domain_id}, projection={'_id': False})
		if domain:
			logger.info(details)
			result = yield self.collection.update_one({'domain_id': domain_id}, {'$set': details}, upsert=False)
			logger.info(result.modified_count)

		else:
				message = {"error": True, "success": False, "message": "Domain doesnt exist"}
		"""
		message = {"error": False, "success": True, "message": __message, "data": "%s with %s has been updated"%(self.module_type, module_id)}
		self.write(message)
		self.finish()
		return 

	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def delete(self, module_id):
		user_id = self.request.arguments.get("user_id")[0].decode("utf-8")
		deletion_approval = self.request.arguments.get("deletion_approval")[0].decode("utf-8")
		#post_arguments = json.loads(self.request.body.decode("utf-8"))
		#user_id = post_arguments.get("user_id", None) ##who created this category
		if not module_id:
			raise Exception("Please send the module id")
		
		module = yield self.module_collection.find_one({"module_id": module_id})
		user = yield self.user_collection.find_one({"user_id": user_id})
		deletion_approval
		pprint (user)
		pprint (user)
		if user["user_type"] == "superadmin":
				if not deletion_approval:
						yield DeleteModule.mark_deletion(self.db, module, self.module_collection, self.child_collection_name, False)			
				else:
					yield DeleteModule.delete_module_n_children_permissions(self.db, module, self.module_collection, self.child_collection_name, self.permission_collection)
					yield DeleteModule.delete_module_n_children(self.db, module, self.module_collection, self.child_collection_name)
				message = {"error": False, "success": True, "message": "Module %s with module_id %s and module_name %s has been \
				deleted"%(self.module_type, module_id, module["module_name"]), "data": module_id}
				self.write(message)
				self.finish()
				return
				

		result = yield Permission.get_permission_delete(user, module, self.permission_collection)
		if result:
			##mark domain and its children under "deletion_approval": pending
			yield DeleteModule.mark_deletion(self.db, module, self.module_collection, self.child_collection_name, True)			
			message = {"error": False, "success": True, "data": "Module %s with module_id %s and module_name %s submitted for deletion and requires superadmin approval\
									"%(self.module_type, module_id, module["module_name"]), "data": module_id}

		else:
			message = "Insufficient permissions"
			self.set_status(400)
			self.write(message)
			self.finish()
			return 
	
		self.write({"data": module_id})
		self.finish()
		return

	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def get(self, module_id=None):
		"""

		Rule: admin will get all the modules but with a permission object attached to it. The permission object for a user 
			only will be present in permissions_collection is somebody having that permission assign it to them. THis poses a problem
			that while fetching these module by admin, no permission object could be found in permission collection, so this can be solved by
			adding a permission object {"get": True, "edit": False, "delete": False, "add_children": False} if nor permission object could 
			be found for admin. This will not be the case with normal user because by default he will only have {"get": True, "edit": True, "delete":False, "add_children": True}
			on the modules which he created, Only this case a permission object has to be added to this user.
		Rule: A user cannot get domains if they are not creation_approval=True by superadmin, But a user who created this domain
			will have this domain.
		"""
		
		user_id = self.request.arguments.get("user_id")[0].decode("utf-8")
		try:
			parent_id = self.request.arguments.get("parent_id")[0].decode("utf-8")
		except Exception:
			parent_id = None
		modules = []
		try:
			skip = self.request.arguments.get("skip")[0].decode("utf-8")
			limit = self.request.arguments.get("limit")[0].decode("utf-8")
		except Exception:
			skip = 0
			limit = 15
		
		try:
			module_id = self.request.arguments.get("module_id")[0].decode("utf-8")
		except Exception:
			module_id= None
		try:
			text_search = self.request.arguments.get("text_search")[0].decode("utf-8")
		except Exception:
			text_search = None

		user = yield self.user_collection.find_one({"user_id": user_id})

		if user["user_type"] == "superadmin":
			if text_search:
				modules = yield self.module_collection.find({"parent_id": parent_id},{"module_name":{"$text":{"$search": text_search}}}, projection={"_id": False}).skip(skip).limit(limit)
			else:
				cursor = self.module_collection.find({"parent_id": parent_id}, projection={"_id": False}).skip(skip).limit(limit)
				while (yield cursor.fetch_next):
					modules.append(cursor.next_object())
			[module.update({"permission": {"get": True, "delete": True, "add_child": True, "edit": True}}) for module in modules]
		
		else:
				modules = yield Permissions.get_modules(user, parent_id, skip, limit, self.module_type, text_search, self.module_collection, self.permission_collection)
		
		#Now the front end nees data in terms of module_ids and modules
		module_ids = []
		_modules = []
		for module in modules:
			module_ids.append(module.get("module_id"))
			try:
				children = len(module.get("children"))
			except Exception as e:
				children = 0
			module.update({"children": children})
			_modules.append(module)
		
		message = {"error": True, "success": False, "message": "Success", "data": {"modules": _modules, "module_ids": module_ids}}
		pprint (message)
		self.write(message)
		self.finish()
		return
