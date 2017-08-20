import tornado.options
import tornado.web
from tornado.escape import json_decode as TornadoJsonDecode
from SettingsModule.settings  import domain_collection_name, indian_time, jwt_secret, \
									 default_document_limit, user_collection_name, permission_collection_name

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

@tornado.gen.coroutine
def add_permission(user_id, module_id, module_name, module_type, rest_parameters, parent_id, 
					granter_id, permission_collection, deletion_approval, creation_approval):
		for (permission, value) in rest_parameters.items():

			yield permission_collection.update_one({"user_id": user_id, 
											"module_id": module_id, 
											"module_name": module_name,
											"module_type": module_type, 
											"parent_id": parent_id,
											"granter_id": granter_id}, 
											{"$set": {permission: value, "deletion_approval": deletion_approval, "creation_approval": creation_approval}}, upsert=True)

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


	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def post():
		post_arguments = json.loads(self.request.body.decode("utf-8"))
		user_id = post_arguments.get("user_id")
		permissions = post_arguments.get("permissions", None)
		module_id = post_arguments.get("module_id", None)
		granter_id = post_arguments.get("granter_id", None)

		user = yield self.user_collection.find_one({"user_id": "granter_id"})
		module = yield self.module_collection.find_one({"module_id": module_id})
		if user["user_type"] == "superadmin" or user["user_type"] == "admin":

				yield add_permission(user_id, module_id, module_name, self.module_type,
								 permissions, 
								 module["parent_id"], granter_id, self.permission_collection)
				result = "permissions updated"
		
		else:
			result = "Insufficient permissions"


		self.write({"error": False, "success": True, "data": result})
		self.finish()
		return 

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
		self.permission_collection = None
		
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
			pprint (user)
			if not user:
				raise Exception("The user who is trying to create this domain doesnt exists")
				


			## checking permissions
			if user["user_type"] != "superadmin" or  not user["user_type"] != "admin":
				pprint (user["user_type"])
				if self.module_type == "domain":
					if not user["create_domain"]:
						raise Exception("The user who is trying to create this domain have insufficient permissions")
			
			if user["user_type"] != "superadmin" or  not user["user_type"] != "admin":
				dummy = yield self.permission_collection.find_one({"module_id": parent_id, "user_id": user_id})["add_child"]
				if not dummy:
						raise Exception("The user who is trying to create this domain have insufficient permissions")
						

			##check if email is already registered with us
			module = yield self.module_collection.find_one({"module_name": module_name})
			if module:
				raise Exception("This module have already been created")

			_id = hashlib.sha1(module_name.encode("utf-8")).hexdigest()
			
			module_id = "%s-%s"%(module_name, _id)
			if self.parent_collection:
					parent_document = yield self.parent_collection.find_one({"module_id": parent_id})
					parent_document["parents"].append({"module_id": parent_id,
																"module_name": parent_document["module_name"] })
					parents = parent_document["parents"]
					##This will add a children to the parent collection
					yield self.parent_collection.update({"module_id": parent_id}, {"$addToSet": \
								{"children": {"module_id": module_id, "module_name": module_name}}}, upsert=False)

			else:
				parents = []


			#TODO
			#A permisssion check will be implemented here to check whether this user even have
			##the permission to make this object

			module = {'module_name': module_name, "description": description, "parent_id": parent_id, "parents": parents,
							 "module_id": module_id, "utc_epoch": time.time(), "indian_time": indian_time(), "username": user["username"],
							 "user_id": user_id, "status": True, "deletion_approval": False, "creation_approval": False, 
							  "module_type": self.module_type, "child_collection_name": self.child_collection_name}
			yield self.module_collection.insert_one(module)



			logger.info("Domain created at %s with domain_id %s"%(indian_time(), _id))
			
			yield add_permission(user_id, module_id, module_name, self.module_type,
								 {"edit": True, "delete": False, "add_child": False, "get": True}, 
								 parent_id, user_id, self.permission_collection, False, False)
			
			
		

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
	def put(self, object_id):
		##TODO if a user has to become a superadmin
		put_arguments = json.loads(self.request.body.decode("utf-8"))
		user_id = put_arguments.get("user_id", None)
        
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
			message = {"error": False, "success": True, "data": "Domain has been updated"}

		else:
				message = {"error": True, "success": False, "message": "Domain doesnt exist"}
		self.write(message)
		self.finish()
		return 

	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def delete(self, module_id):
		post_arguments = json.loads(self.request.body.decode("utf-8"))
		user_id = post_arguments.get("user_id", None) ##who created this category

		result = yield self.permission_collection.find_one({"user_id": user_id, "module_id": module_id, "delete": True})
		if result:
			#now this domain and all its children will have delete_pending approval 
			module = yield self.module_collection.find_one({"module_id": module_id})
			if module["deletion_approval"]:
				##delete domain and its all children
				yield self.module_collection.update_one({"module_id": module_id})
				yield mark_children(module["children"], module["child_collection_name"])

			else:
				##mark domain and its children under "deletion_approval": pending
				yield self.module_collection.update_one({"module_id": module_id}, {"$set": {"deletion_approval": "pending"}}, upsert=False)
				yield mark_children(module["children"], module["child_collection_name"])

		else:
			result = "Insufficient permissions"		
	
		result = yield self.collection.find_one_and_delete({'domain_id': domain_id})
		logger.info(result)
		message = {"error": False, "success": True, "data": message}
		#TODO: delete all parmissions as well
		self.write(message)
		self.finish()
		return

	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def get(self, module_id):
		#user = self.check_user(user_id)
		get_arguments = json.loads(self.request.body.decode("utf-8"))
		user_id = get_arguments.get("user_id", None) ##who created this category
		

		user = yield self.user_collection.find_one({"user_id": user_id})

		##Now if a  a user is superadmin, he will get all the modules whether they are approved or not
		if user["user_type"] == "superadmin":
				result = yield self.module_collection.find({"module_id": module_id})
				if not result:
					message = "No %ss exists"%self.module_type
					result = []
					

		##if a user is admin, he will get all the modules only if they are approved
		if user["user_type"] == "admin":
				result = yield self.module_collection.find({"module_id": module_id, "creation_approval" : True})
				if not result:
					
					message = "No %ss exists"%self.module_type
					result = []


		if user["user_type"] != "superadmin" or user["user_type"] != "admin":
			##if a user is neither admin or superadmin, a permission check has to be done to check the get: true for this user_id
			result = yield self.permission_collection.find_one({"user_id": user_id, "module_id": module_id, "get": True, 
								"module_type": self.module_type ,"get": True, "deletion_approval": False, 
						"creation_approval": True})

			if not result :
				message = "Insufficient permissions for any %ss"%self.module_type
				result = []

			else:
				modules = []
				for document in result:
					doc = yield self.module_collection.find_one({"module_id": document.get("module_id")}, projection={"_id": False} )
					modules.append(doc)
				result = {"module_ids": module_ids, "modules": modules}
				message = "success"

		message = {"error": True, "success": False, "message": message, "data": result}
		self.write(message)
		pprint (message)
		self.finish()
		return 


