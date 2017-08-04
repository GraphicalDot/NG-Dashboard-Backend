import tornado.options
import tornado.web
from tornado.escape import json_decode as TornadoJsonDecode
from SettingsModule.settings  import indian_time, jwt_secret, \
									 default_document_limit
from SettingsModule.settings  import subject_collection_name as collection_name
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





@tornado.gen.coroutine
def delete_children(ontology_id, db, children_collection_name):
	ids = [ontology_id]
	for collection in db[children_collection_name]:
		for _id in ids:
			ids = yield collection.find_many_and_delete({"parent_id": _id})
		  




#@auth
class ParentOntology(tornado.web.RequestHandler):
	def initialize(self):
		self.db = self.settings["db"]
		self.collection = self.db[collection_name]
		self.name = name
		self.id_name = "%s_id"%self.name
		self.parent_collection = None
		self.child_collection = None

	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def options(self, nanoskill_id=None):
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
		ontology_name = post_arguments.get("ontology_name", None)
		description = post_arguments.get("description", None)
		user_type = post_arguments.get("user_type")
		parent_id = post_arguments.get("parent_id", None)
		##Permissions
		##For the user other 
		
		#user = yield db[credentials].find_one({'user_type': user_type, "username": username, "password": password})
		
		try:
			if None in [ontology_name, description]:
				raise Exception("Fields shouldnt be empty")

			if user_type != "superadmin":
				raise Exception("Only superadmin can nanoskills")




			##check if email is already registered with us
			user = yield self.collection.find_one({"name": ontology_name})
			if user:
				raise Exception("This %s have already been created"%ontology_name)

			_id = hashlib.sha1(ontology_name.encode("utf-8")).hexdigest()


			ontology_document = {'name': ontology_name, "description": description, "parent_id": parent_id,\
							 self.id_name : _id,"utc_epoch": time.time(), "indian_time": indian_time()}
			yield self.collection.insert_one(ontology_document)

			logger.info("ontology_name %s created at %s with id %s"%(ontology_name, indian_time(), _id))
			
			
			
		

			#TODO: will be used to send email to the user
			##executor.submit(task, datetime.datetime.now())
		except Exception as e:
				logger.error(e)
				self.write({"error": True, "success": False, "message": e.__str__()})
				self.finish()
				return 

		##This line has to be added, somehow while inserting nanoskill into the mongo, nanoskill itself got a new _id key
		##which is not serializable
		print (ontology_document.pop("_id"))
		##TODO : implement JWT tokens
		self.write({"error": False, "success": True, "data": ontology_document})
		self.finish()
		return 




	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def put(self, ontology_id):
		##TODO if a user has to become a superadmin
		ontology_document = yield self.collection.find_one({self.id_name: ontology_id}, projection={'_id': False})
		if user:
			logger.info(ontology_document)
			result = yield self.collection.update_one({self.id_name: ontology_id}, {'$set': details})
			message = {"error": False, "success": True, "message": "ontology has been updated"}

		else:
				message = {"error": True, "success": False, "message": "ontology with id %s doesnt exist"%ontology_id}
		self.write(message)
		self.finish()
		return 

	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def delete(self, ontology_id):
		result = yield self.collection.find_one({self.id_name: ontology_id}, projection={'_id': False})
		if result:
				result = yield self.collection.find_one_and_delete({'ontology_id': ontology_id})
				logger.info(result)
				delete_children(ontology_id, self.db, self.children_collection_name)
				
				message = {"error": False, "success": True, "message": "ontology has been deleted"}


		else:
				message = {"error": True, "success": False, "message": "ontology doesnt exist"}

		#TODO: delete all parmissions as well
		self.write(message)
		self.finish()
		return

	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def get(self, ontology_id=None):
		#user = self.check_user(user_id)
		if ontology_id:
				ontology_document = yield self.collection.find_one({self.id_name: ontology_id}, projection={'_id': False})
		else:
				ontology_document = yield self.collection.find(projection={'_id': False}).to_list(length=100)
			

		if ontology_document:
				message = {"error": False, "success": True, "message": None, "data": ontology_document}

		else:
				message = {"error": True, "success": False, "message": "No document exist"}

		self.write(message)
		self.finish()
		return 


class Subjects(ParentOntology):
	def initialize(self):
		self.db = self.settings["db"]
		self.collection = self.db[collection_name]
		self.name = "subject"
		self.id_name = "%s_id"%self.name
		self.parent_collection = None
		self.child_collection = None