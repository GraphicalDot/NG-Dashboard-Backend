import tornado.options
import tornado.web
from tornado.escape import json_decode as TornadoJsonDecode
from SettingsModule.settings  import concept_collection_name, indian_time, jwt_secret, \
									 default_document_limit, domain_collection_name, \
									 domain_permissions, concept_permissions
from LoggingModule.logging import logger
import time 
import hashlib
from pprint import pprint
import jwt
import json
from AuthenticationModule.authentication import auth
#https://emptysqua.re/blog/refactoring-tornado-coroutines/
## finding user from motor  yields a future object which is nothing but a promise that it will have a value in future
## and gen.coroutine is a perfect to resolve a future object uyntillit is resolved

import codecs

from generic.cors import cors
reader = codecs.getreader("utf-8")




def ConceptPermissions(tornado.web.RequestHandler):
	def initialize(self):
		self.db = self.settings["db"]
		self.collection = self.db[domain_collection_name]
		self.user_collection = self.db[user_collection_name]
		self.concept_permissions = self.db[concept_permissions]
		self.domain_permissions = self.db[domain_permissions]
		self.subconcept_permissions = self.db[subconcept_permissions]


	def post(self):
		post_arguments = json.loads(self.request.body.decode("utf-8"))
		granter_id =post_arguments.get("granter_id") 
		concept_id = post_arguments.get("concept_id")
		user_id = post_arguments.get("user_id")
		permissions = post_arguments.get("permissions")
		#permission = {"add_child": True, "edit": True, "delete": True, "get": True}

		##add_chld permission will be checked in concept creation
		#edit includes changin permissions as well
		if granter_id == "superadmin":
			yield self.domain_permissions.insert({"user_id": user_id, "domain_id": domain_id})

		user = yield self.user_collection.find_one({"user_id": user_id})
		
		if user["is_admin"]:
			yield self.concept_permissions.insert({"user_id": user_id, "concept_id": concept_id})
			

		try:
			if not yield self.domain_permissions.find_one({"user_id": user_id, "domain_id": domain_id})["permissions"]["edit"]:
				raise Exception ("Insufficient permissions")

			yield self.domain_permissions.insert({"user_id": user_id, "domain_id": domain_id, "granter_id": granter_id, "permissions": permissions})

		except Exception as e:
				logger.error(e)
				self.set_status(400)
				self.write({"error": True, "success": False, "token": None, "message": e.__str__()})
				self.finish()
				return 

		##This line has to be added, somehow while inserting nanoskill into the mongo, nanoskill itself got a new _id key
		##which is not serializable
		##TODO : implement JWT tokens
		self.write({"error": False, "success": True, "data": domain})
		self.finish()
		return 



#@auth
class Concepts(tornado.web.RequestHandler):

	def initialize(self):
		self.db = self.settings["db"]
		self.collection = self.db[concept_collection_name]
		self.domain_collection = self.db[domain_collection_name]
		self.domain_permissions = self.db[domain_permissions]
		self.concept_permissions = self.db[concept_permissions]
	
	
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
		print (self.request.body)
		post_arguments = json.loads(self.request.body.decode("utf-8"))
		concept_name = post_arguments.get("concept_name", None)
		description = post_arguments.get("description", None)
		user_type = post_arguments.get("user_type")
		parent_id = post_arguments.get("parent_id")
		parent_name = post_arguments.get("parent_name")
		connections = post_arguments.get("connections", None)
		bloom_taxonomy = post_arguments.get("bloom_taxonomy", None)
		difficulty_level= post_arguments.get("difficulty_level", None)
		required_domains = post_arguments.get("required_domains", None)

		user_name = post_arguments.get("user_name")
		user_id = post_arguments.get("user_id")
		##Permissions
		##For the user other 
		
		#user = yield db[credentials].find_one({'user_type': user_type, "username": username, "password": password})
		
		try:
			if None in [concept_name, description, user_name, user_type, parent_id]:
				raise Exception("Fields shouldnt be empty")

			if user_type != "superadmin":
				raise Exception("Only superadmin can make domains")




			##check if email is already registered with us
			user = yield self.collection.find_one({"concept_name": concept_name})
			if user:
				raise Exception("This domain have already been created")

			if not yield self.domain_permissions({"user_id": user_id, "domain_id": parent_id})["permissions"]["add_child"]:
				raise Exception("The user doesnt have sufficient permissions to create concepts for this domain")

			_id = hashlib.sha1(concept_name.encode("utf-8")).hexdigest()


			"""
			if category_permissions:
					a = CategoriesPermissions()
					yield a.update_permissions(self.db, user_id, category_permissions)
			"""
			concept = {'concept_name': concept_name, "description": description, "parent_name": parent_name, \
							 "concept_id": _id,"utc_epoch": time.time(), "indian_time": indian_time(), "parent_id": parent_id, 
							 "connections": connections, "difficulty_level": difficulty_level,
							 "required_domains": required_domains, "user_name": user_name,
							 "bloom_taxonomy": bloom_taxonomy, "user_id": user_id
							 }
			yield self.collection.insert_one(concept)

			logger.info("Concept created at %s with concept_id %s"%(indian_time(), _id))
			yield self.concept_permissions.insert({"user_id": user_id, "parent_id": parent_id, "concept_id": _id
				 "granter_id": user_id, "permissions": {"add_child": True, "edit": True, "delete": True, "get": True}})

			
			
		

			#TODO: will be used to send email to the user
			#TODO: Put checks on checking parent_id
			#TODO put check on the existence of the uers
			##executor.submit(task, datetime.datetime.now())
		except Exception as e:
				logger.error(e)
				self.write({"error": True, "success": False, "token": None, "message": e.__str__()})
				self.finish()
				return 

		##This line has to be added, somehow while inserting nanoskill into the mongo, nanoskill itself got a new _id key
		##which is not serializable
		##TODO : implement JWT tokens
		concept.pop("_id")
		self.write({"error": False, "success": True, "data": concept})
		self.finish()
		return 




	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def put(self, domain_id):
		##TODO if a user has to become a superadmin
		details = json.loads(self.request.body.decode("utf-8"))
		
		domain = yield self.collection.find_one({"domain_id": domain_id}, projection={'_id': False})
		if domain:
			logger.info(details)
			result = yield self.collection.update_one({'domain_id': domain_id}, {'$set': details})
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
	def delete(self, concept_id):
		result = yield self.collection.find_one({"concept_id": concept_id}, projection={'_id': False})
		if result:
				result = yield self.collection.find_one_and_delete({'concept_id': concept_id})
				logger.info(result)
				message = {"error": False, "success": True, "message": "concept has been deleted"}
		else:
				message = {"error": True, "success": False, "message": "concept doesnt exist"}

		#TODO: delete all parmissions as well
		self.write(message)
		self.finish()
		return

	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def get(self, concept_id=None):
		#user = self.check_user(user_id)
		if concept_id:
				concept = yield self.collection.find({"concept_id": concept_id}, projection={'_id': False})
		else:
				_result = yield self.collection.find(projection={'_id': False}).to_list(length=100)
				object_ids = []
				objects = []
				for _object in _result:
					object_ids.append(_object.get("concept_id"))
					objects.append(_object)
				result = {"concepts": objects,"concept_ids": object_ids}


			

		if result:
				message = {"error": False, "success": True, "message": None, "data": result}

		else:
				message = {"error": True, "success": False, "message": "No nanoskills exist"}

		self.write(message)
		pprint(message)
		self.finish()
		return 



