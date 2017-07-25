import tornado.options
import tornado.web
from tornado.escape import json_decode as TornadoJsonDecode
from SettingsModule.settings  import nanoskill_collection_name, indian_time, jwt_secret, \
									 default_document_limit
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



#@auth
class Nanoskills(tornado.web.RequestHandler):

	def initialize(self):
		self.db = self.settings["db"]
		self.collection = self.db[nanoskill_collection_name]
	
	
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
		name = post_arguments.get("name", None)
		description = post_arguments.get("description", None)
		user_type = post_arguments.get("user_type")
		##Permissions
		##For the user other 
		
		#user = yield db[credentials].find_one({'user_type': user_type, "username": username, "password": password})
		
		try:
			if None in [name, description]:
				raise Exception("Fields shouldnt be empty")

			if user_type != "superadmin":
				raise Exception("Only superadmin can nanoskills")




			##check if email is already registered with us
			user = yield self.collection.find_one({"name": name})
			if user:
				raise Exception("This nanoskill have already been created")

			_id = hashlib.sha1(name.encode("utf-8")).hexdigest()


			"""
			if category_permissions:
					a = CategoriesPermissions()
					yield a.update_permissions(self.db, user_id, category_permissions)
			"""
			nanoskill = {'name': name, "description": description,\
							 "nanoskill_id": _id,"utc_epoch": time.time(), "indian_time": indian_time()}
			yield self.collection.insert_one(nanoskill)

			logger.info("Nanoskill created at %s with nanoskill_id %s"%(indian_time(), _id))
			
			
			
		

			#TODO: will be used to send email to the user
			##executor.submit(task, datetime.datetime.now())
		except Exception as e:
				logger.error(e)
				self.write({"error": True, "success": False, "token": None, "message": e.__str__()})
				self.finish()
				return 

		##This line has to be added, somehow while inserting nanoskill into the mongo, nanoskill itself got a new _id key
		##which is not serializable
		print (nanoskill.pop("_id"))
		##TODO : implement JWT tokens
		self.write({"error": False, "success": True, "data": nanoskill})
		self.finish()
		return 




	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def put(self, nanoskill_id):
		##TODO if a user has to become a superadmin
		user = yield self.collection.find_one({"nanoskill_id": nanoskill_id}, projection={'_id': False})
		if user:
			logger.info(details)
			result = yield self.collection.update_one({'nanoskill_id': nanoskill_id}, {'$set': details})
			logger.info(result.modified_count)
			message = {"error": False, "success": True, "message": "User has been updated"}

		else:
				message = {"error": True, "success": False, "message": "User doesnt exist"}
		self.write(message)
		self.finish()
		return 

	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def delete(self, nanoskill_id):
		result = yield self.collection.find_one({"nanoskill_id": nanoskill_id}, projection={'_id': False})
		if result:
				result = yield self.collection.find_one_and_delete({'nanoskill_id': nanoskill_id})
				logger.info(result)
				message = {"error": False, "success": True, "message": "nanoskill has been deleted"}
		else:
				message = {"error": True, "success": False, "message": "nanoskill doesnt exist"}

		#TODO: delete all parmissions as well
		self.write(message)
		self.finish()
		return

	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def get(self, nanoskill_id=None):
		#user = self.check_user(user_id)
		if nanoskill_id:
				user = yield self.collection.find_one(projection={'_id': False})
		else:
				user = yield self.collection.find(projection={'_id': False}).to_list(length=100)
			

		if user:
				message = {"error": False, "success": True, "message": None, "data": user}

		else:
				message = {"error": True, "success": False, "message": "No nanoskills exist"}

		self.write(message)
		print (message)
		self.finish()
		return 

