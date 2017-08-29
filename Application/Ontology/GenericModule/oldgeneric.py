import tornado.options
import tornado.web
from tornado.escape import json_decode as TornadoJsonDecode
from SettingsModule.settings  import domain_collection_name, indian_time, jwt_secret, \
									 default_document_limit, user_collection_name, permission_collection_name, \
									 action_collection_name

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

from generic.cors import cors
from pprint import pprint
reader = codecs.getreader("utf-8")

"""
new_collection 

	user_id, module_id, module_name, permission_type, parent_id 





"""
#About permissions, permission collcetion will have the permissions listed in it.
#there will a granter_id who grants the permission, A user_id who receives the permissions
## And the get, edit, delete, add_child permissions that can be granted, While providing the permissions in 
## put requests in permission param, It will be checked as in permissions who have True flags will only be updated, 

@tornado.gen.coroutine
def add_permission(user_id, module_id, module_name, module_type, rest_parameters, parent_id, 
					granter_id, permission_collection):
		for (permission, value) in rest_parameters.items():
			logger.info("permission <<%s>> with value <<%s>> from granter_id %s to user_id %s"%(permission, value, granter_id, user_id))
			yield permission_collection.update_one({"user_id": user_id, 
											"module_id": module_id, 
											"module_name": module_name,
											"module_type": module_type, 
											"parent_id": parent_id,
											"granter_id": granter_id}, 
											{"$set": {permission: value}}, upsert=True)

		return 



@tornado.gen.coroutine
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



@tornado.gen.coroutine
def mark_children(db, children, child_collection_name):
	collection = db[child_collection_name]
	for child in children:
		child = yield collection.find_one({"module_id": child["module_id"]})
		delete_id = yield collection.update_one({"module_id": child["module_id"]}, {"deletion_approval": "pending"}, upsert=False)
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


@tornado.gen.coroutine
def actions(name_action_by, id_action_by, name_action_on, id_action_on, action, action_collection):
		action_collection.update_one({
					"name_action_by": name_action_by,
					"id_action_by": id_action_by,
					"name_action_on": name_action_on,
					"id_action_on": id_action_on,
					"action": action,
					}, upsert=True)


class GenericPermissions(tornado.web.RequestHandler):

	def initialize(self):
		self.db = self.settings["db"]
		self.parent_collection = None
		self.parent_name = None
		self.module_collection = None
		self.user_collection = None
		self.module_type = None
		self.child_collection = None
		self.permission_collection = None
		self.child_collection_name = None
		self.action_collection = None

	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def get(self, module_id):
		post_arguments = json.loads(self.request.body.decode("utf-8"))
		user_id = post_arguments.get("user_id", None)

		if not user_id:
			result = yield self.permission_collection.find({"module_id": module_id}, projection={"_id": False}).tolist(100)
		else:
			result = yield self.permission_collection.find({"user_id": user_id, "module_id": module_id}, projection={"_id": False}).tolist(100)
			

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
		
		try:
			if None in [module_name, description, user_id]:
				raise Exception("Fields shouldnt be empty")

			user = yield self.user_collection.find_one({"user_id": user_id})
			if not user:
				raise Exception("The user who is trying to create this domain doesnt exists")
				

			##if module type is domain then user either must be superadmin, admin or must have create_domain  permissions on the parent	
			if self.module_type == "domain":
				if user["user_type"] != "superadmin" or  not user["user_type"] != "admin":
					if not user["create_domain"]:
						raise Exception("The user who is trying to create this domain have insufficient permissions")
			
			## If module is not domain, A user must be superadmin, admin or have add_child perissions on the parent domain
			else:
				if not parent_id:
						raise Exception("Please provide a parent_id to create %s"%self.module_type)
				else:
					if user["user_type"] != "superadmin" or  not user["user_type"] != "admin":
						dummy = yield self.permission_collection.find_one({"module_id": parent_id, "user_id": user_id, "add_child": True})
						if not dummy:
								raise Exception("The user who is trying to create this %s have insufficient permissions"%self.module_type)
				
			##check if email is already registered with us
			module = yield self.module_collection.find_one({"module_name": module_name})
			if module:
				raise Exception("This module have already been created")

			_id = hashlib.sha1(module_name.encode("utf-8")).hexdigest()
			
			module_id = "%s-%s"%(self.module_type, _id)
			logger.info(module_id)
			if self.parent_collection:
					parent_document = yield self.parent_collection.find_one({"module_id": parent_id})

					if not parent_document:
						raise Exception("The parent id with id %s doesnt exists"%parent_id)
					##this is to ensure that child can only be made once its aproved by superadmin
					if not parent_document["creation_approval"] or parent_document["deletion_approval"] == "pending":
						raise Exception("Parent module creation first shall be approved by superadmin or its deletion is pending")

					parent_document["parents"].append({"module_id": parent_id,
																"module_name": parent_document["module_name"] })
					parents = parent_document["parents"]
					##This will add a children to the parent collection
					yield self.parent_collection.update({"module_id": parent_id}, {"$addToSet": \
								{"children": {"module_id": module_id, "module_name": module_name}}}, upsert=False)

			else:
				parents = []

			pprint (parents)
			##As this module is created by superadmin, it will not need any creation_approval approval
			if user["user_type"] == "superadmin":
				creation_approval = True
			else: 
				creation_approval = False
				

			#TODO
			#A permisssion check will be implemented here to check whether this user even have
			##the permission to make this object

			##deletion approval is False just after creation, If a user with delete permission wants to delete this module, 
			## It will be subjected to approval by superadmin, he can approve or disapprove its deletion, 
			## when a user submits its request to delete certain module, its status becomes pending
			module = {'module_name': "%s-%s"%(self.module_type, module_name), "description": description, "parent_id": parent_id, "parents": parents,
							 "module_id": module_id, "utc_epoch": time.time(), "indian_time": indian_time(), "username": user["username"],
							 "user_id": user_id, "status": True, "deletion_approval": False, "creation_approval": creation_approval, 
							  "module_type": self.module_type, "child_collection_name": self.child_collection_name, "children": []}
			yield self.module_collection.insert_one(module)

			pprint (module)
			

			logger.info("%s created at %s with module_id %s"%(self.module_type, indian_time(), module_id))
			
			if user["user_type"] != "superadmin":
				yield add_permission(user_id, module_id, module_name, self.module_type,
								 {"edit": True, "delete": False, "add_child": False, "get": True}, 
								 parent_id, user_id, self.permission_collection)
			
			
		

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
		put_arguments = json.loads(self.request.body.decode("utf-8"))
		user_id = put_arguments.get("user_id") ##User to whom the permissions will be provided
		granter_id = put_arguments.get("granter_id") ##who is changing the permissions of this module
		permission = put_arguments.get("permission", None)
		creation_approval = put_arguments.get("creation_approval", None)
		module_data = put_arguments.get("module_data", None)

		pprint (put_arguments)
		try:
			__message = None
			module = yield self.module_collection.find_one({"module_id": module_id})
			granter = yield self.user_collection.find_one({"user_id": granter_id})
			user = yield self.user_collection.find_one({"user_id": user_id})
			if not user:
				raise Exception("This user doesnt exists")


			##actual deletion will be handled in delete request, which will delete the module and its children
			if module["deletion_approval"] == "pending":
				raise Exception("Deletion is pending for this module by superadmin")


			if creation_approval == "delete":
				if user["user_type"] == "superadmin":
							yield self.module_collection.delete({"module_id": module_id})
							yield self.permission_collection.delete_many({"module_id": module_id})
				else:
					raise Exception("Only superadmin can change creation approval status")			

			if creation_approval == True:
				if user["user_type"] == "superadmin":
							yield self.module_collection.update_one({"module_id": module_id}, {"$set": {"creation_approval": True}}, upsert=False)
							yield self.permission_collection.update_many({"module_id": module_id}, {"$set": {"creation_approval": True}}, upsert=False)
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
				if not granter["user_type"]:
					for rest_paramter in ["get", "delete", "edit", "add_child"]:
						if permission[rest_paramter]:
							result = yield self.permission_collection.find({"user_id": granter_id, "module_id": module_id, rest_paramter: True, 
									"module_type": self.module_type}, 
									projection={"_id": False}).to_list(100)
							if not result:
								__message.append("Insufficient permissions to provide %s permission"%rest_paramter)
							else:
								yield add_permission(user_id, module_id, module["module_name"], self.module_type,
								 {rest_paramter: True}, 
								 module["parent_id"], granter_id, self.permission_collection)
								 
				##is granter is superadmin or admin, all permissions will be added to the user
				else:

								pprint ("Adding permission by superadmin or admin")
								yield add_permission(user_id, module_id, module["module_name"], self.module_type,
								 permission, 
								 module["parent_id"], granter_id, self.permission_collection)



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
		#post_arguments = json.loads(self.request.body.decode("utf-8"))
		#user_id = post_arguments.get("user_id", None) ##who created this category
		if not module_id:
			raise Exception("Please send the module id")
		
		module = yield self.module_collection.find_one({"module_id": module_id})
		user = yield self.user_collection.find_one({"user_id": user_id})
		
		pprint (user)
		pprint (user)
		if user["user_type"] == "superadmin":
				pprint ("executing from super admin %s"%self.module_type)
				yield self.module_collection.delete_one({"module_id": module_id})
				yield delete_children(self.db, module["children"], module["child_collection_name"])
				message = {"error": False, "success": True, "data": "Module %s with module_id %s and module_name %s has been \
				deleted"%(self.module_type, module_id, module["module_name"])}
				pprint (message)
				#TODO: delete all parmissions as well
				self.write(message)
				self.finish()
				return
				

		result = yield self.permission_collection.find_one({"user_id": user_id, "module_id": module_id, "delete": True})
		
		if result:
			#now this domain and all its children will have delete_pending approval 
			if module["deletion_approval"]:
				##delete domain and its all children
				yield self.module_collection.delete_one({"module_id": module_id})
				yield delete_children(self.db, module["children"], module["child_collection_name"])
				message = {"error": False, "success": True, "data": "Module %s with module_id %s and module_name %s has been \
				deleted"%(self.module_type, module_id, module["module_name"])}

			else:
				##mark domain and its children under "deletion_approval": pending
				yield self.module_collection.update_one({"module_id": module_id}, {"$set": {"deletion_approval": "pending"}}, upsert=False)
				yield mark_children(self.db, module["children"], module["child_collection_name"])
				message = {"error": False, "success": True, "data": "Module %s with module_id %s and module_name %s submitted for deletion and requires superadmin approval\
									"%(self.module_type, module_id, module["module_name"])}

		else:
			message = "Insufficient permissions"
			self.set_status(400)
			self.write(message)
			self.finish()
			return 
	
		#result = yield self.collection.find_one_and_delete({'domain_id': domain_id})
		logger.info(result)
		pprint ({"data": module_id})
			
		#TODO: delete all parmissions as well
		self.write({"data": module_id})
		self.finish()
		return

	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def get(self, module_id=None):
		#user = self.check_user(user_id)
		#post_arguments = json.loads(self.request.body.decode("utf-8"))
		pprint (self.request.arguments)
		pprint (self.request.body)
		
		user_id = self.request.arguments.get("user_id")[0].decode("utf-8")

		try:
			parent_id = self.request.arguments.get("parent_id")[0].decode("utf-8")
		except Exception as e:
			parent_id = None

		@tornado.gen.coroutine
		def if_superadmin(module_id, parent_id, user_id, module_type):
			pprint ("super admin function")
			if module_id:
				pprint ("module_id found")
				result = yield self.module_collection.find_one({"module_id": module_id}, projection={"_id": False})
			result = yield self.module_collection.find({"module_type": module_type, "parent_id": parent_id}, projection={"_id": False}).to_list(100)
			if not result:
				raise Exception ("No %ss exists"%self.module_type)
			return result
		@tornado.gen.coroutine
		def if_admin(module_id, parent_id, user_id, module_type):
			pprint ("admin function")
			if module_id:
				result = yield self.module_collection.find_one({"module_id": module_id, "creation_approval": True,
																"module_type": module_type,  "deletion_approval": False})
			result = yield self.module_collection.find({"creation_approval": True, "parent_id": parent_id,
																	"module_type": module_type,	"deletion_approval": False}, 
																	projection={"_id": False}).to_list(100)
			if not result:
				raise Exception ("No %ss exists"%self.module_type)
			return result


		@tornado.gen.coroutine
		def generic_user(module_id, parent_id, user_id, module_type):
			pprint ("generic user  function")
			

			if module_id:
				result = yield self.permission_collection.find_one({"user_id": user_id, "module_id": module_id, "get": True, 
							"module_type": self.module_type , "deletion_approval": False, 
						"creation_approval": True})
				if not result:
					raise Exception ("Insufficeint permissions to get %s "%module_id)
				return result
				
			#huge code changes required as parent_id = None for domain is to be fetched same for other modules
			##
			result = yield self.permission_collection.find({"user_id": user_id, "get": True, "module_type": self.module_type ,
			}, projection={"_id": False}).to_list(100)
			
			print (result)
			return result



		try:

			#get_arguments = json.loads(self.request.body.decode("utf-8"))
			##pprint (get_arguments)
			#user_id = get_arguments.get("user_id", None) ##who created this category
			if not user_id:
				raise Exception("Please bear the pain to send user_id")
			user = yield self.user_collection.find_one({"user_id": user_id})
			if not user:
				raise Exception("This user doesnt exists")

			##Now if a  a user is superadmin, he will get all the modules whether they are approved or not
			if user["user_type"] == "superadmin":
				__result = yield if_superadmin(module_id, parent_id, user_id, self.module_type)					

			if user["user_type"] == "admin":
				__result = yield if_admin(module_id, parent_id,  user_id, self.module_type)					

			if user["user_type"] == "superadmin" or user["user_type"] == "admin":
				modules = []
				module_ids = []
				for document in __result:
					modules.append(document)
					module_ids.append(document.get("module_id"))						
				result = {"module_ids": module_ids, "modules": modules}


			if not user["user_type"]:
				__result = yield generic_user(module_id, parent_id, user_id, self.module_type)					
				if __result:
					module_ids = []
					modules = []
					for document in __result:
						doc = yield self.module_collection.find_one({"module_id": document.get("module_id"), "deletion_approval": False}, projection={"_id": False} )
						modules.append(doc)
					result = {"module_ids": module_ids, "modules": modules}
				else:
					result = []
			message = "success"
			
		except Exception as e:
			logger.error(e)
			message = str(e)
			self.set_status(500)
			self.write(e.__str__())
			self.finish()
			return 
		pprint (result)
		message = {"error": True, "success": False, "message": message, "data": result}
		self.write(message)
		logger.info(message)
		self.finish()
		return
