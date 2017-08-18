import tornado.options
import tornado.web
from tornado.escape import json_decode as TornadoJsonDecode
from SettingsModule.settings  import domain_collection_name, indian_time, jwt_secret, \
									 default_document_limit, user_collection_name, domain_permissions,\
                                     concepts_permissions, subconcepts_permissions,nanoskill_permissions,\
                                     question_permissions, domain_collection_name, concept_collection_name,\
                                     subconcept_collection_name, nanoskill_collection_name, question_collection_name
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


def GenericPermissions(tornado.web.RequestHandler):
	def initialize(self):
		self.db = self.settings["db"]
		self.collection = self.db[domain_collection_name]
		self.user_collection = self.db[user_collection_name]
		self.collection_permissions = self.db[domain_permissions]


def update_permissions(collection=None, user_collection=None, collection_permissions=None,
                    granter_id=None, object_id=None, user_id=None, permissions, object_name=None):

        #collection could be collection of domain, concept, subconcept, nanoskill, question
        ##collection permission could be of type domain_permissions, concept_permissions etc
        ##granter_id is the user id of the user who wants to grant permission to some other user.
        ##object_id is the domain_id, concept_id, question_id etc
        ##permissions is the object of type {"add_child": True, "read": True, "edit": True, "delete": True}
		#permission = {"add_child": True, "edit": True, "delete": True, "get": True}

		##add_chld permission will be checked in concept creation
		#edit includes changin permissions as well
		if granter_id == "superadmin":
			yield self.domain_permissions.insert({"user_id": user_id, "%s_id"%(object_name): object_id})

		user = yield self.user_collection.find_one({"user_id": user_id})
		
		if user["is_admin"]:
			yield self.collection_permissions.insert({"user_id": user_id, "%s_id"%(object_name): object_id})
			

		try:
			if not yield self.collection_permissions.find_one({"user_id": user_id, "%s_id"%(object_name): object_id})["permissions"]["edit"]:
				raise Exception ("Insufficient permissions")

			yield self.domain_permissions.insert({"user_id": user_id, "%s_id"%(object_name): object_id, "granter_id": granter_id,
                         "permissions": permissions})

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

def create_object(user=None, object_name=None, parent_id=None, object_id=None, 
                parent_permissions):
    ## Only in the case of domain, a user will have root permissions
    ## Other than domain. A user have to have add_child permissions on the parent
    if object_name = "domain":
        if not user["root_permissions"]:
	        pprint ("The user who is trying to create this domain have insufficient permissions")
            return False

    ##This will check the user has add_child permission on the parent to add this object
    if not yield self.parent_permissions.find_one({"user_id": user_id, "object_id": object_id})["permissions"]["add_child"]:
        return False

    return 


def delete_edit_permissions(request_type=None, user_id=None, collection_permissions=None, user_collection=None, object_id=None):
    ##while deleting, edit and get, three conditions has to be checked, is this user a superamdin
    ## is this user a admin
    ## or s/he has required permissions
    ##request_type: edit, delete, get
    if user_id == "superadmin":
        return True

    if yield user_collection.find_one({"user_id", user_id}, projection={"_id": False})["is_admin"]:
        return True

    if not yield self.collection_permissions.find_one({"user_id": user_id, "object_id": object_id})["permissions"][request_type]:
        return False




def delete_action(user_id=None, collection= None, parent_collection=None, collection_permissions=None,
                                                                             child_collection=None):
        ##if only delete_edit_permissions is True, this action will be executed
        if yield collection.find_one({"user_id": user_id, "object_id": object_id})["approved"]:
            #This implies that superadmin approved its deletion, so delete this object_id and its chlidren
            ##also delete this object_id entry in permission_collection and its child permission collection
            yield collection.delete_one({"object_id": object_id})
            for __collection in child_collection:
                yield __collection.delete_many({"object_id": object_id}) 
        
            for __collection in self.child_permission:
                yield __collection.delete_many({"object_id": object_id}) 

        self.child_collection

                yield domains.update_one({"user_id": user_id, "domain_id": domain_id, {"$set": {"status": False, "approved": False}}})
                yield concepts.update_one({"user_id": user_id, "domain_id": domain_id, {"$set": {"status": False, "approved": False}}})
                yield subconcepts.update_one({"user_id": user_id, "domain_id": domain_id, {"$set": {"status": False, "approved": False}}})
                yield nanoskills.update_one({"user_id": user_id, "domain_id": domain_id, {"$set": {"status": False, "approved": False}}})
                yield questions.update_one({"user_id": user_id, "domain_id": domain_id, {"$set": {"status": False, "approved": False}}})
    
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
			



def edit_action():



def get_objects(user_id=None, collection=None, collection_permissions=None, user_collection=None, object_id=None):

    if not collection.find_one({"object_id": object_id}):
        return False

    if not user_collection.find_one({"user_id": user_id}):
        return False


    if object_id:
        if not yield self.collection_permissions.find_one({"user_id": user_id, "object_id": object_id})["permissions"]["get"]:
            return []

    result = yield self.collection_permissions.find_many({"user_id": user_id, "object_id": object_id}, projection={"_id": False})
    
    if user_id == "superadmin":
        return collection.find_many({"user_id": user_id}, projection={"_id": False}) 

    if yield user_collection.find_one({"user_id", user_id}, projection={"_id": False})["is_admin"]:
        return collection.find_many({"user_id": user_id}, projection={"_id": False}) 
    
    object_ids = []
    for _object in result:
            if _object["permissions"]["get"]:
                object_ids.appned(_object.get("object_id"))

    return  yield self.collection_permissions.find_many({"user_id": user_id, "object_id": object_id, "permissions.get": True}, projection={"_id": False})


#@auth
class Domains(tornado.web.RequestHandler):

	def initialize(self):
		self.db = self.settings["db"]
        self.parent_collection = None
		self.collection = self.db[domain_collection_name]
        self.child_collection = [self.db[concept_collection_name], 
                                self.db[subconcept_collcection_name], 
                                self.db[nanoskill_collcection_name], 
                                self.db[question_collcection_name]
                                ]
		self.user_collection = self.db[user_collection_name]
		self.collection_permission = self.db[domain_permissions]
        
        self.child_permission = [self.db[concept_permissions], 
                                self.db[subconcept_permissions], 
                                self.db[nanoskill_permissions], 
                                self.db[question_permissions]
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
		post_arguments = json.loads(self.request.body.decode("utf-8"))
		domain_name = post_arguments.get("domain_name", None)
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
            object_id = "domain-%s"%_id

			#TODO
			#A permisssion check will be implemented here to check whether this user even have
			##the permission to make this object

			domain = {'name': domain_name, "description": description,\
							 "object_id": object_id,"utc_epoch": time.time(), "indian_time": indian_time(), "user_name": user_name, 
							 "user_id": user_id, "status": True}
			yield self.collection.insert_one(domain)

			##The domain which is created will have this user as its admin i.e has all the permissions
			yield self.collcetion_permissions.insert({"user_id": user_id, "object_id": object_id,
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
	def delete(self, object_id):
        post_arguments = json.loads(self.request.body.decode("utf-8"))
		user_id = post_arguments.get("user_id", None) ##who created this category
		def check(user_id, domain_id):	
			
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
	def get(self, object_id):
		#user = self.check_user(user_id)
        get_arguments = json.loads(self.request.body.decode("utf-8"))
		user_id = get_arguments.get("user_id", None) ##who created this category
        result = yield get_objects(user_id=user_id, collection=self.collection, 
                    collection_permissions=self.collection_permissions, 
                    user_collection=self.user_collection, 
                    object_id=object_id)

        if not result:
            message = "Either domain or user doesnt exists"
		else:
			message = {"error": True, "success": False, "message": None, "data": result}

		self.write(message)
		print (message)
		self.finish()
		return 


