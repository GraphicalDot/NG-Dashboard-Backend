import tornado.options
import tornado.web
from SettingsModule.settings import user_collection_name, domain_collection_name, template_collection_name,\
					indian_time, variable_collection_name
from LoggingModule.logging import logger
from tornado.ioloop import IOLoop
import hashlib
import jwt
import json 
from pprint import pprint 
import uuid
import time
import math

#https://emptysqua.re/blog/refactoring-tornado-coroutines/
## finding user from motor  yields a future object which is nothing but a promise that it will have a value in future
## and gen.coroutine is a perfect to resolve a future object uyntillit is resolved

from GeneralModule.cors import cors

def make_ngrams(word, min_size=2):
		"""
		basestring       word: word to split into ngrams
		int   min_size: minimum size of ngrams
		"""
		length = len(word)
		size_range = range(min_size, max(length, min_size) + 1)
		return list(set(
			word[i:i + size]
			for size in size_range
			for i in range(0, max(0, length - size) + 1)
			))


class Variables(tornado.web.RequestHandler):
	#TODO: Need to implement users whoc can make variables
	def initialize(self):
			self.db = self.settings["db"]
			self.variable_collection = self.db[variable_collection_name]
			self.user_collection = self.db[user_collection_name]

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
	def  get(self):
		user_id = self.request.arguments.get("user_id")[0].decode("utf-8")
		try:
			skip = int(self.request.arguments.get("skip")[0].decode("utf-8"))
			limit = int(self.request.arguments.get("limit")[0].decode("utf-8"))
		except Exception:
			skip = 0
			limit = 15
		
		try:
			variable_id = self.request.arguments.get("variable_id")[0].decode("utf-8")
		except Exception:
			variable_id= None
		try:
			search_text = self.request.arguments.get("search_text")[0].decode("utf-8")
		except Exception:
			search_text = None

		user = yield self.user_collection.find_one({"user_id": user_id})

		
		variables = []
		if search_text:
				variable_count = yield self.variable_collection.find({ 
							"$text":{"$search": search_text}}, projection={"_id": False, "ngrams": False}).count()
				
				pprint ("This is the template count %s"%variable_count)
				cursor = self.variable_collection.find({
							"$text":{"$search": search_text}}, projection={"_id": False, "ngrams": False}).skip(skip).limit(limit)
				while (yield cursor.fetch_next):
					variables.append(cursor.next_object())
			
		else:
				variable_count = yield self.variable_collection.find(projection={"_id": False, "ngrams": False}).count()
				cursor = self.variable_collection.find(projection={"_id": False, "ngrams": False}).skip(skip).limit(limit)
				while (yield cursor.fetch_next):
					variables.append(cursor.next_object())

		variable_ids = []
		for module in variables:
			module.pop("user_id")
			module.pop("utc_epoch")
			variable_ids.append(module.get("variable_id"))

		message = {"error": True, "success": False, "message": "Success", "data": {"variables": variables, "variable_ids": variable_ids, 
						"variable_count": variable_count, "pages": math.ceil(variable_count/limit)}}

		pprint (message)
		self.write(message)
		self.finish()
		return


	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def  delete(self):
		user_id = self.request.arguments.get("user_id")[0].decode("utf-8")
		variable_id = self.request.arguments.get("variable_id")[0].decode("utf-8")
		try:
			#post_arguments = json.loads(self.request.body.decode("utf-8"))
			#user_id = post_arguments.get("user_id", None) ##who created this category
			if not variable_id:
				raise Exception("Please send the variable id")
		
			variable = yield self.variable_collection.find_one({"variable_id": variable_id})
			user = yield self.user_collection.find_one({"user_id": user_id})
			if user["user_type"] == "superadmin":
				yield self.variable_collection.delete_one({"variable_id": variable_id})
			else:
				raise Exception("You have insufficient permissions to delete this module")
		
		except Exception as e:
			print (e)
			self.set_status(403)
			self.write(str(e))
			self.finish()
			return 


		message = {"data": variable_id}
		print (message)
		self.write(message)
		self.finish()
		return

	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def  post(self):
		"""
		Used to create a new user or update and existing one
		Request Param:
			user_type: admin, accessor, evaluator, superadmin
			username: 
			password: 
			newpassword:
		"""

		print (self.request.body)
		post_arguments = json.loads(self.request.body.decode("utf-8"))
		print (post_arguments)
		variable_name = post_arguments.get("variable_name")
		description = post_arguments.get("description")
		user_id = post_arguments.get("user_id")
		data_type = post_arguments.get("data_type")
		identifier = post_arguments.get("identifier")
		categories = post_arguments.get("categories")
		#user = yield db[credentials].find_one({'user_type': user_type, "username": username, "password": password})
		
		try:
			user = yield self.user_collection.find_one({"user_id": user_id}, projection={"_id": False, "username": True, "user_type": True})
			if not user:
				raise Exception("This user doesnt exists")
			
			
			if not user["user_type"] == "superadmin":
				if not user["variable"]:
					raise Exception("You dont have sufficient permissions to create variables")
				

			if not variable_name or not identifier:
				raise Exception("Variable Name or identifier is missing")

			if not identifier.startswith("#"):
				raise Exception("Identifier must starts with #")



			variable_object = yield self.variable_collection.find_one({"variable_name": variable_name}, projection={"_id": False, "variable_name": True})
			if variable_object:
				raise Exception("variable has already been made, Please select a diffrent name for the variable")

			_id = str(uuid.uuid4())

			if user["user_type"] == "superadmin":
				creation_approval = True
			else:
				creation_approval = False

			for category in categories:
				category.update({"category_id": str(uuid.uuid4()) })
				category.update({"images": []})

			variable_object = {"variable_id": _id, "variable_name": variable_name,  "utc_epoch": time.time(), "description": description,
									"indian_time": indian_time(), "ngrams": " ".join(make_ngrams(variable_name)),
									"user_id": user_id, "identifier": identifier, "data_type": data_type, "categories": categories, 
									"creation_approval": False, "username": user["username"]}

			yield self.variable_collection.insert_one(variable_object)
		
		except Exception as e:
				logger.error(e)
				self.set_status(401)
				self.write(e.__str__())
				#self.write({"error": False, "success": True})
				self.finish()
				return 

		variable_object.pop("_id")
		variable_object.pop("user_id")
		variable_object.pop("utc_epoch")
		message = {"error": False, "success": True, "data": {"variable": variable_object, "variable_id": variable_object["variable_id"]}}
		pprint (message)
		self.write(message)
		self.finish()
		return 


