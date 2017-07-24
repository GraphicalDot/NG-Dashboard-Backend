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

reader = codecs.getreader("utf-8")



@auth
class Nanoskills(tornado.web.RequestHandler):

	def initialize(self):
		self.db = self.settings["db"]
		self.collection = self.db[nanoskill_collection_name]	


	
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
			user = yield self.collection.insert_one({'name': name, "description": description,\
							 "nanoskill_id": _id,"utc_epoch": time.time(), "indian_time": indian_time()})

			logger.info("Nanoskill created at %s with nanoskill_id %s"%(indian_time(), _id))
			
			
			
		
			#TODO: will be used to send email to the user
			##executor.submit(task, datetime.datetime.now())
		except Exception as e:
				logger.error(e)
				self.write({"error": True, "success": False, "token": None, "message": e.__str__()})
				self.finish()
				return 

		##TODO : implement JWT tokens
		self.write({"error": False, "success": True, "nanoskill_id": _id})
		self.finish()
		return 



	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def put(self, nanoskill_id):
		##TODO if a user has to become a superadmin
		user = yield self.collection.find_one({"nanoskill_id": nanoskill_id}, projection={'_id': False})
		if user:
				details = { k: self.get_argument(k) for k in self.request.arguments if k not in ["state", "region"]}

				state = self.request.arguments.get("state")
				region = self.request.arguments.get("region") 

				if state:
						state =  list(map(lambda x: x.decode("utf-8"), state))
						details["state"] = state
				if region:
						region = list(map(lambda x: x.decode("utf-8"), region)) 
						details["region"] = region

				if not bool(details):
						message = {"error": True, "success": False, "message": "Nothing to update"}
						self.write(message)
						self.finish()
						return 
						

				logger.info(details)
				result = yield self.collection.update_one({'user_id': user_id}, {'$set': details})
				logger.info(result.modified_count)
				message = {"error": False, "success": True, "message": "User has been updated"}

		else:
				message = {"error": True, "success": False, "message": "User doesnt exist"}
		self.write(message)
		self.finish()
		return 


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

	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def get(self, nanoskill_id):
		print (nanoskill_id)
		print ("Hey rAM")
		#user = self.check_user(user_id)
		user = yield self.collection.find(projection={'_id': False}).to_list(length=100)
		
		if user:
				message = {"error": False, "success": True, "message": None, "nanoskill": user}

		else:
				message = {"error": True, "success": False, "message": "nanoskill doesnt exist"}

		self.write(message)
		self.finish()
		return 

