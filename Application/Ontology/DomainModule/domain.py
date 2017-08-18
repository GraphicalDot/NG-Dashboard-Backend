import tornado.options
import tornado.web
from tornado.escape import json_decode as TornadoJsonDecode
from SettingsModule.settings  import domain_collection_name, indian_time, jwt_secret, \
									 default_document_limit, user_collection_name
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
reader = codecs.getreader("utf-8")


def DomainPermissions(tornado.web.RequestHandler):
	def initialize(self):
		self.db = self.settings["db"]
		self.collection = self.db[domain_collection_name]
		self.user_collection = self.db[user_collection_name]
		self.domain_permissions = self.db[domain_permissions]


	def post(self):
		post_arguments = json.loads(self.request.body.decode("utf-8"))
		granter_id =post_arguments.get("granter_id") 
		domain_id = post_arguments.get("domain_id")
		user_id = post_arguments.get("user_id")
		permissions = post_arguments.get("permissions")
		#permission = {"add_child": True, "edit": True, "delete": True, "get": True}

		##add_chld permission will be checked in concept creation
		#edit includes changin permissions as well
		if granter_id == "superadmin":
			yield self.domain_permissions.insert({"user_id": user_id, "domain_id": domain_id})

		user = yield self.user_collection.find_one({"user_id": user_id})
		
		if user["is_admin"]:
			yield self.domain_permissions.insert({"user_id": user_id, "domain_id": domain_id})
			

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



"""
user: 
	permissions: 
			domains:
				domain_id:
					{"edit": True, "delete": False, "add_child": False, "get": True}
				domain_id:
					{"edit": True, "delete": False, "add_child": False, "get": True}
			concepts:
				concept_id:
					{"edit": True, "delete": False, "add_child": False, "get": True}
													





domain: 
	permissions:
		user_id: 
			{"edit": True, "delete": False, "add_child": False, "get": True}
		user_id:
			{"edit": False, "delete": False, "add_child": True, "get": True}
		

	parent_id: None




concept: 
	permissions:
		user_id: 
			{"edit": True, "delete": False, "add_child": False, "get": True}
		user_id:
			{"edit": False, "delete": False, "add_child": True, "get": True}
		

	parent_id: domain_id

Rules:
	1. To add a child to a parent, A user must have a add_child permission on the parent
	2. A user can only pass paermission to a user, if he himself have those permissions
	3. If a user delete something, It must first be approved by superadmin

"""

#@auth
class Domains(tornado.web.RequestHandler):

	def initialize(self):
		self.db = self.settings["db"]
		self.parent_collection = None
		self.module_collection = self.db[domain_collection_name]
		self.user_collection = self.db[user_collection_name]
		self.module_name = "domain"
		self.child_collection = [self.db[concept_collection_name], 
								self.db[subconcept_collection_name],
								self.db[nanoskill_collection_name], 
								self.db[question_collcection_name]
									]

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
		name = post_arguments.get("name", None)
		description = post_arguments.get("description", None)
		user_type = post_arguments.get("user_type")
		user_id = post_arguments.get("user_id")
		user_name = post_arguments.get("user_name")
		##Permissions
		##For the user other 
		
		#user = yield db[credentials].find_one({'user_type': user_type, "username": username, "password": password})
		
		try:
			if None in [domain_name, description, user_id, user_name]:
				raise Exception("Fields shouldnt be empty")

			user = yield self.user_collection.find_one({"user_name": user_name, "user_id": user_id})
			if not user:
				raise Exception("The user who is trying to create this domain doesnt exists")
				
			if not user["root_permissions"]:
				raise Exception("The user who is trying to create this domain have insufficient permissions")
				

			##check if email is already registered with us
			domain = yield self.collection.find_one({"domain_name": domain_name})
			if domain:
				raise Exception("This domain have already been created")

			_id = hashlib.sha1(domain_name.encode("utf-8")).hexdigest()

			#TODO
			#A permisssion check will be implemented here to check whether this user even have
			##the permission to make this object

			"""
			if category_permissions:
					a = CategoriesPermissions()
					yield a.update_permissions(self.db, user_id, category_permissions)
			"""
			domain = {'domain_name': domain_name, "description": description,\
							 "domain_id": _id,"utc_epoch": time.time(), "indian_time": indian_time(), "user_name": user_name, 
							 "user_id": user_id, "status": True}
			yield self.collection.insert_one(domain)

			##The domain which is created will have this user as its admin i.e has all the permissions
			yield self.domain_permissions.insert({"user_id": user_id, "domain_id": domain_id,
				 "granter_id": user_id, "permissions": {"add_child": True, "edit": True, "delete": True, "get": True}})

			logger.info("Domain created at %s with domain_id %s"%(indian_time(), _id))
			
			
			
		

			#TODO: will be used to send email to the user
			##executor.submit(task, datetime.datetime.now())
		except Exception as e:
				logger.error(e)
				self.set_status(400)
				self.write({"error": True, "success": False, "token": None, "message": e.__str__()})
				self.finish()
				return 

		##This line has to be added, somehow while inserting nanoskill into the mongo, nanoskill itself got a new _id key
		##which is not serializable
		##TODO : implement JWT tokens
		domain.pop("_id")
		self.write({"error": False, "success": True, "data": domain})
		self.finish()
		return 




	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def put(self, domain_id):
		##TODO if a user has to become a superadmin
		details = json.loads(self.request.body.decode("utf-8"))
		if not yield self.domain_permissions.find_one({"user_id": user_id, "domain_id": domain_id})["permissions"]["edit"]:
			raise Exception ("Insufficient permissions")
		
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
	def delete(self, domain_id):

		def check(user_id, domain_id):	
			if "user_id" == "superadmin":
                return True

            ##this means that this domains deletion requests has already been submitted and now its approved by superadmin
            if yield domain_permissions.find_one({"user_id": user_id, "domain_id": domain_id, "approved": True}):
                yield domain_permissions.delete({"domain_id": domain_id})
                yield concepts_permissions.delete({"domain_id": domain_id})
                yield subconcepts_permissions.delete({"domain_id": domain_id})
                yield nanoskill_permissions.delete({"domain_id": domain_id})
                yield question_permissions.delete({"domain_id": domain_id})
                
                #delet Domain and its children here
                return True #implies that its ok to delete domain and its children

            #If the domain is deleted all teh child for this domain even created by other users will be deleted
            ##if the above case is not true, then domain deleteion is then subjected to admin approval and its 
            # status become inactive and all its children, The trick is inactive status has to be posted on original collections
            if yield domain_permissions.find_one({"user_id": user_id, "domain_id": domain_id})["permissions"]["delete"]:
                yield domains.update_one({"user_id": user_id, "domain_id": domain_id, {"$set": {"status": False, "approved": False}}})
                yield concepts.update_one({"user_id": user_id, "domain_id": domain_id, {"$set": {"status": False, "approved": False}}})
                yield subconcepts.update_one({"user_id": user_id, "domain_id": domain_id, {"$set": {"status": False, "approved": False}}})
                yield nanoskills.update_one({"user_id": user_id, "domain_id": domain_id, {"$set": {"status": False, "approved": False}}})
                yield questions.update_one({"user_id": user_id, "domain_id": domain_id, {"$set": {"status": False, "approved": False}}})
                return False
            else:
                raise Exception("Insufficient permissions")
            return #its not ok to delete the domain

		try:

			result = check()
			if result:
				yield self.collection.find_one_and_delete({'domain_id': domain_id})
				yield self.concept_collection.delete_many({'domain_id': domain_id})
				yield self.subconcept_collection.delete_many({'domain_id': domain_id})
				yield self.nanoskill_collection.delete_many({'domain_id': domain_id})
				yield self.question_collection.delete_many({'domain_id': domain_id})
				yield self.domain_permissions.delete_many({'domain_id': domain_id})
				yield self.concept_permissions.delete_many({'domain_id': domain_id})
				yield self.subconcept_permissions.delete_many({'domain_id': domain_id})
				yield self.nanoskill_permissions.delete_many({'domain_id': domain_id})
				yield self.question_permissions.delete_many({'domain_id': domain_id})
				data = "domain and its hicldren has been removed"
			else:
				data = "domain and its children willbe removed after approval from superadmin"
		except Exception as e:
			data = str(e)
			message = {"error": True, "success": False, "data": message}
			
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
	def get(self):
		#user = self.check_user(user_id)
		domain_ids = yield self.domain_permissions.find({"user_id": user_id, "permissions.get": True}, projection={"domain_id": True, "_id": False})
		_result = []
		for _id in domain_ids:
				f = yield self.collection.find_one({"domain_id": _id}, projection={'_id': False})
				_result.append(f)

		_result = yield self.collection.find(projection={'_id': False}).to_list(length=100)
		object_ids = []
		objects = []
			for _object in _result:
				object_ids.append(_object.get("domain_id"))
				objects.append(_object)
			result = {"domains": objects,"domain_ids": object_ids}



		if result:
				message = {"error": False, "success": True, "message": None, "data": result}

		else:
				message = {"error": True, "success": False, "message": "No domains exist"}

		self.write(message)
		print (message)
		self.finish()
		return 

