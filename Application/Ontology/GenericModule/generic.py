import tornado.options
import tornado.web
from tornado.escape import json_decode as TornadoJsonDecode
from SettingsModule.settings  import domain_collection_name, indian_time, jwt_secret, \
									 default_document_limit, user_collection_name, permission_collection_name, \
									 action_collection_name, question_types

import operator
from .delete_module import DeleteModule
from .permissions import Permissions
from LoggingModule.logging import logger
import time 
import hashlib
import jwt
import json
import math
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
If a user creates a domain, He will have all the permissions on this module

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
	def post(self):
		post_arguments = json.loads(self.request.body.decode("utf-8"))

		try:
			user_id = post_arguments.get("user_id") 
			user = yield self.user_collection.find_one({"user_id": user_id})

			target_user_id = post_arguments.get("target_user_id") 
			target_user = yield self.user_collection.find_one({"user_id": target_user_id})
			
			if not user or not target_user:
					raise Exception("No user exists")


			parent_id = post_arguments.get("parent_id") 
			##Because domain has no parent
			if parent_id == None and self.module_type != "domain":
				raise Exception("Please provide the parent_id")

			module_id = post_arguments.get("module_id") 
			module = yield self.module_collection.find_one({"module_id": module_id})
			if not module:
					raise Exception("No module exists")


			permission = post_arguments.get("permission") 
			pprint(permission)
			
			assert isinstance(permission, dict), 'permissions shall of dict  type!'


			if user["user_type"] == "superadmin":
				pprint ("Adding permission by superadmin")
				yield Permissions.set_permission_from_obj(target_user, module, permission, parent_id, 
									user, self.permission_collection)

			else:
				##First check if the user_id has sufficient permission on the module or not,
				pprint ("Adding permission by user_type who is not superadmin")
				for rest_parameter in ["get", "delete", "edit", "add_child"]:
					if permission[rest_parameter]:
						result = yield Permissions.get_permission_rest_parameter(user, module, rest_parameter, self.permission_collection)
						if not result:
							raise Exception("Insufficient permissions to provide %s permission"%rest_parameter)
						else:
							print ("user_type <<%s>> with user_id<<%s>> have %s on %s"%(granter["user_type"], granter["user_id"], rest_parameter, module["module_id"]))
							yield Permissions.set_permission_rest_paramter(target_user, module, parent, user, rest_parameter, self.permission_collection)



		except Exception as e:
				logger.error(e)
				self.set_status(400)
				self.write(e.__str__())
				self.finish()
				return 

		##This line has to be added, somehow while inserting nanoskill into the mongo, nanoskill itself got a new _id key
		##which is not serializable				assert isinstance(permission, dict), 'permissions shall of dict  type!'
		##TODO : implement JWT tokens
		self.write({"error": False, "success": True, "data": permission})
		self.finish()
		return 
						





	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def get(self):

		"""
		For permissions of a logged in user on every module can be obtained from the get request of egenric class.
		Now a different need is, A superadmin or any other user could pass on permission to other user.
		For this, A module_id will be given and all the permissions for several user must be provided int he response. 

		So for example, 
			case 1: superadmin
					supeadmin have all the permissions, 
					so ehen clicking on the +permission , a user list will be populated, superadmin will select a 
					user and with this user_is and module_id a requst will be made onto this class.

					Now, A user will have permissions for this module, which will be generated in form of checkboxes intot he 
					front end, In case a superadmin want to change a specific permission, He will click on the checkbox
					A request will be made onto the put request


			case 2: A general user 
					Only the module on which a user will have get permission will be shown to the user.
					same process of user selection and module selection follows.

					Same ui will be generated after a response from this api, Except for the fact that
					the permission on hich the user id doesnt have Tre will be freezed, so user_id cnnot change these
					permisison for target user.

		"""
		try:
			user_id = self.request.arguments.get("user_id")[0].decode("utf-8")
			user = yield self.user_collection.find_one({"user_id": user_id})
			if not user:
					raise Exception("No user exists")
					
			target_user_id = self.request.arguments.get("user_id")[0].decode("utf-8")
			target_user = yield self.user_collection.find_one({"user_id": user_id})
			if not target_user:
					raise Exception("No target user exists")
		
			try:
				skip = self.request.arguments.get("skip")[0].decode("utf-8")
				limit = self.request.arguments.get("limit")[0].decode("utf-8")
			except Exception:
				skip = 0
				limit = 15	

			module_id = self.request.arguments.get("module_id")[0].decode("utf-8")
			
			if module_id:
				##Only the permissions of this module_id must be given in the response.
				
				pprint ("This is the module_id %s"%module_id)
				module = yield self.module_collection.find_one({"module_id": module_id})
				if not module:
					raise Exception("Module doesnt exists")
				else:
					result = yield Permissions.user_module_permission(module, target_user, self.permission_collection)
			else:
				## All the permission of the target module for all the users  has to be given fot his module_type,
				result = yield Permissions.get_permissions_module(skip, limit, user, module, permission_collection, user_collection)

		except Exception as e:
				logger.error(e)
				self.set_status(400)
				self.write(e.__str__())
				self.finish()
				return 

		##This line has to be added, somehow while inserting nanoskill into the mongo, nanoskill itself got a new _id key
		##which is not serializable
		##TODO : implement JWT tokens
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
		pprint (parents)
					##This will add a children to the parent collection
		result = yield self.parent_collection.update({"module_id": parent_id}, {"$addToSet": \
			{"children": {"module_id": module_id, "module_name": module_name}}}, upsert=False)


		return parents


	def make_ngrams(self, word, min_size=2):
		"""
		basestring       word: word to split into ngrams
		int   min_size: minimum size of ngrams
		"""
		if not word:
			return []

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
	def  post(self):
		if not self.request.body:
			raise Exception("Dude! I need some data")
		post_arguments = json.loads(self.request.body.decode("utf-8"))
		module_name = post_arguments.get("module_name", None)
		description = post_arguments.get("description", None)
		user_id = post_arguments.get("user_id")
		parent_id  = post_arguments.get("parent_id")
		
		bloom_taxonomy = post_arguments.get("bloom_taxonomy")
		prereq_modules_all_parents = post_arguments.get("prereq_modules_all_parents")
		prereq_modules = post_arguments.get("prereq_modules")
		difficulty = post_arguments.get("difficulty")


        ##Permissions
		##For the user other 
		
		#user = yield db[credentials].find_one({'user_type': user_type, "username": username, "password": password})
		pprint (self.module_type)		
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

			module_name = "%s-%s"%(self.module_type, module_name)
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

			if self.module_type == "question":
				pprint ("This is the module type Question")
				question_text = "No Content yet"
				question_type = post_arguments.get("question_type")
				''' 
				if question_type not in question_types:
					raise Exception("Specify a valid question type")
				if options == []:
					raise Exception("options for question shouldnt be left empty")
				'''		
				
				##this is to index all parents of this question, so a search can be build on the parents of this question
				parent_ngrams = []
				for parent in parents:
					parent_ngrams.extend(parent.get("module_name"))

				print ("I reached here")
				module = {'module_name': module_name, "description": description, "parent_id": parent_id, "parents": parents,
							 "module_id": module_id, "utc_epoch": time.time(), "indian_time": indian_time(), "username": user["username"],
							 "user_id": user_id, "status": True, "deletion_approval": False, "creation_approval": creation_approval, "parent_name": parent_module["module_name"],
							  "module_type": self.module_type, "user_type": user["user_type"], "child_collection_name": self.child_collection_name, "children": [],
								"ngrams": " ".join(self.make_ngrams(module_name) + self.make_ngrams(question_text)), 
							  "question_text": question_text,
							  "question_type": question_type,
							  "options": [],
							  "images": {},
							  }
				print (module)

			else:

				#TODO
				module = {'module_name': module_name, "description": description, "parent_id": parent_id, "parents": parents,
							 "module_id": module_id, "utc_epoch": time.time(), "indian_time": indian_time(), "username": user["username"],
							 "user_id": user_id, "status": True, "deletion_approval": False, "creation_approval": creation_approval, 
							  "module_type": self.module_type, "user_type": user["user_type"], "child_collection_name": self.child_collection_name, "children": [],
							  "ngrams": " ".join(self.make_ngrams(module_name)), 
							  "prereq_modules": prereq_modules,
							  "prereq_modules_all_parents": prereq_modules_all_parents,
							  "bloom_taxonomy": bloom_taxonomy, 
							  "difficulty": difficulty
							  
							  }
			
			
			if self.module_type == "nanoskill":
				skip_nanoskills = post_arguments.get("skip_nanoskills")
				print ("Updating nannoskills with skip nannoskill as %s"%skip_nanoskills)
				module.update({"skip_nanoskills": skip_nanoskills})

			result = yield self.module_collection.insert_one(module)
			pprint (result)
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
				self.write( e.__str__())
				self.finish()
				return 

		##This line has to be added, somehow while inserting nanoskill into the mongo, nanoskill itself got a new _id key
		##which is not serializable
		##TODO : implement JWT tokens
		module.pop("_id")
		module.pop("ngrams")
		
		#because in get request we are sending in the length of the children array
		module["children"] = 0
		##adding permission to this newly created module, If a user is superadmin he will have all the permissions
		## If a user is creater he will have all the permissions on it.

		permission = {'add_child': True, 'delete': True, 'edit': True, 'get': True}
		module["permission"] = permission
		self.write({"error": False, "success": True,  "data":
										 {"module": module, 
										"module_id": module["module_id"],
										"message": "%s with name %s has been added"%(self.module_type, module["module_name"]), 
										}})
		self.finish()
		return 




	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def put(self):
		##TODO if a user has to become a superadmin
		##On the frontend "children" key gets converted to 0 rather then [], changing while updating the document
		put_arguments = json.loads(self.request.body.decode("utf-8"))
		#pprint (put_arguments)

		edituser = put_arguments.get("user") ##User to whom the permissions will be provided
		editmodule = put_arguments.get("module")

		try:
			editmodule.pop("permission")
		except Exception:
			pass
		try:
			__message = None
			module = yield self.module_collection.find_one({"module_id": editmodule["module_id"]})
			user = yield self.user_collection.find_one({"user_id": edituser["user_id"]})
			if not user:
				raise Exception("This user doesnt exists")

			if not module:
				raise Exception("This module doesnt exists")
				
			pprint ("reached here 460")

			##NO idea why we are converting children key to empty list, possible reason db has children as empty list
			if user["user_type"] == "superadmin":
				if editmodule["children"] == 0:
						editmodule["children"] = []
			else:
				##THis is to check if another user is trying to create approval a module
				if not module["creation_approval"]:
					if editmodule["creation_approval"]:
						raise Exception("Only a superadmin can approvae a creation of %s"%self.module_type)		
						

				if not Permissions.get_permission_rest_parameter(edituser, editmodule, "edit", self.permission_collection):
					raise Exception("You have insufficient Permissions")		

			if self.module_type == "question":
					images = module["images"]
					
					editmodule.update({"images": images})

			pprint ("reached here")
			try:
				editmodule.pop("permission")
			except Exception:
				pass


			yield self.module_collection.update_one({"module_id": editmodule["module_id"]}, {"$set": editmodule}, upsert=False)


		except Exception as e:
				logger.error(e)
				self.set_status(400)
				self.write(e.__str__())
				self.finish()
				return 
	
		message = {"error": False, "success": True,  "data": {"module": editmodule, "message": "%s with %s has been updated"%(self.module_type, editmodule["module_id"])}}
		pprint (message)
		self.write(message)
		self.finish()
		return 

	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def delete(self):
		"""
			If superadmin makes an request, Everything will be deleted, Module entry from the parent sand 
			all its chidren and all the enteries of this module and its children in the permission collection.abs

			If a user is not superadmin, if this user has delete permission on the module then the deletion_approval will become 
			True, in this case, which will then pass onto superadmin for deletion, If the delete_approval is true this domain and its children and its entry in the parent 
			wil not be shown to any users except to the superadmin and the user who created it. (Provision has to be made to make it deleteion_approval =False) for any user
			who would have edit request on this module
		"""

		pprint (self.request.arguments)
		user_id = self.request.arguments.get("user_id")[0].decode("utf-8")
		module_id = self.request.arguments.get("module_id")[0].decode("utf-8")
		try:
			#post_arguments = json.loads(self.request.body.decode("utf-8"))
			#user_id = post_arguments.get("user_id", None) ##who created this category
			if not module_id:
				raise Exception("Please send the module id")
		
			module = yield self.module_collection.find_one({"module_id": module_id})
			user = yield self.user_collection.find_one({"user_id": user_id})
			if user["user_type"] == "superadmin":
				print ("Ohh fuck the user is superadmin")
				yield DeleteModule.delete_module(self.db, module, self.module_collection, self.child_collection_name, 
						self.parent_collection, self.permission_collection)

				message = "Module %s with module_id %s and module_name %s has been deleted"%(self.module_type, module_id, module["module_name"])
				self.write({"error": False, "success": True, "data": {"module_id": module_id, "message": message}})
				self.finish()
				return
				

			result = yield Permissions.get_permission_rest_parameter(user, module, "delete", self.permission_collection)
			pprint(result)
			if result:
			##mark domain and its children under "deletion_approval": pending
				yield DeleteModule.mark_module(self.db, module, self.module_collection, self.child_collection_name, 
						self.parent_collection, self.permission_collection)

			
				message = "Module %s with module_id %s and module_name %s submitted for deletion and requires superadmin approval\
									"%(self.module_type, module_id, module["module_name"])
				self.write({"error": False, "success": True, "data": {"module_id": module_id, "message": message}})
				self.finish()
				return

			else:
				message = "Insufficient permissions"
				self.set_status(400)
				self.write(message)
				self.finish()
				return 
		except Exception as e:
			print (e)
			self.set_status(403)
			self.write(str(e))
			self.finish()
			return 

		pprint (module_id)
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
			skip = int(self.request.arguments.get("skip")[0].decode("utf-8"))
			limit = int(self.request.arguments.get("limit")[0].decode("utf-8"))
		except Exception:
			skip = 0
			limit = 15
		
		try:
			module_id = self.request.arguments.get("module_id")[0].decode("utf-8")
		except Exception:
			module_id= None
		try:
			search_text = self.request.arguments.get("search_text")[0].decode("utf-8")
		except Exception:
			search_text = None

		user = yield self.user_collection.find_one({"user_id": user_id})

		
		if user["user_type"] == "superadmin":
			modules = []
			if search_text:
				module_count = yield self.module_collection.find({"parent_id": parent_id, 
							"$text":{"$search": search_text}}, projection={"_id": False, "ngrams": False}).count()
				
				pprint ("This is the module count %s"%module_count)
				cursor = self.module_collection.find({"parent_id": parent_id,
							"$text":{"$search": search_text}}, projection={"_id": False, "ngrams": False}).sort("children", -1).skip(skip).limit(limit)
				while (yield cursor.fetch_next):
					modules.append(cursor.next_object())
			
			else:
				module_count = yield self.module_collection.find({"parent_id": parent_id}, projection={"_id": False, "ngrams": False}).count()
				cursor = self.module_collection.find({"parent_id": parent_id}, projection={"_id": False, "ngrams": False}).sort("children", -1).skip(skip).limit(limit)
				while (yield cursor.fetch_next):
					modules.append(cursor.next_object())
			[module.update({"permission": {"get": True, "delete": True, "add_child": True, "edit": True}}) for module in modules]
		
		else:
				modules, module_count = yield Permissions.get_modules(user, parent_id, skip, limit, self.module_type, search_text, self.module_collection, self.permission_collection)
		
		#Now the front end nees data in terms of module_ids and modules
		module_ids = []
		_modules = []
		for module in modules:

			module_ids.append(module.get("module_id"))
			try:
				children = len(module.get("children"))
			except Exception as e:
				print (e)
			module.update({"children": children})
			_modules.append(module)
		
		_modules = sorted(_modules,  key= lambda x: x["children"], reverse=True)

		pprint ("skip == <<%s>> and limit = <<%s>>"%(skip, limit))
		message = {"error": True, "success": False, "message": "Success", "data": {"modules": _modules, "module_ids": module_ids, 
						"module_count": module_count, "pages": math.ceil(module_count/limit)}}

		pprint (message)
		self.write(message)
		self.finish()
		return


class Allmodules(tornado.web.RequestHandler):


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


	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def get(self):
		parent_id = self.request.arguments.get("parent_id")[0].decode("utf-8")
		print (parent_id)
		modules = []
		try:
			search_text = self.request.arguments.get("search_text")[0].decode("utf-8")
		except Exception:
			search_text = None

		try:
			skip = self.request.arguments.get("skip")[0].decode("utf-8")
		except Exception:
			skip = 0
		try:
			limit = self.request.arguments.get("limit")[0].decode("utf-8")
		except Exception:
			limit = 1000

		
		if search_text:
				module_count = yield self.module_collection.find({"parent_id": { "$ne": parent_id },  
							"$text":{"$search": search_text}}, projection={"_id": False, "module_name": True, "module_id": True}).count()
				
				pprint ("This is the module count %s"%module_count)
				cursor = self.module_collection.find({"parent_id": { "$ne": parent_id }, "$text":
						{"$search": search_text}}, projection={"_id": False, "module_name": True, "module_id": True}).sort("children", -1).skip(skip).limit(limit)
				while (yield cursor.fetch_next):
					modules.append(cursor.next_object())
			
		else:
				module_count = yield self.module_collection.find({"parent_id": { "$ne": parent_id } }, projection={"_id": False, "module_name": True, "module_id": True}).count()
				cursor = self.module_collection.find({"parent_id": { "$ne": parent_id } },projection={"_id": False, "module_name": True, "module_id": True}).sort("children", -1).skip(skip).limit(limit)
				while (yield cursor.fetch_next):
					modules.append(cursor.next_object())
		
		
		#Now the front end nees data in terms of module_ids and modules
		
		pprint (module_count)
		message = {"error": True, "success": False, "message": "Success", "data":  modules}

		self.write(message)
		self.finish()
		return



