import tornado.options
import tornado.web
from SettingsModule.settings import user_collection_name, domain_collection_name, template_collection_name,  indian_time
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


class TemplateSkeleton(tornado.web.RequestHandler):

	def initialize(self):
			self.db = self.settings["db"]
			self.template_collection = self.db[template_collection_name]

	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def  get(self):
		domains = []
		cursor = self.db[domain_collection_name].find(projection={"_id": False, "module_id": True, "module_name": True, "child_collection_name": True })
		while (yield cursor.fetch_next):
			domains.append(cursor.next_object())
			
		result = []
		for domain in domains:
			name = domain.pop("module_name")
			_id = domain.pop("module_id")
			domain.update({"name": name, "id": _id})

			child_collection_name = domain.pop("child_collection_name")


			children = yield Templates.get_children(domain, self.db, child_collection_name)
			domain.update({"children": children})
			result.append(domain)


		self.write({"error": False, "success": True, "data": result})
		self.finish()
		return 

class Templates(tornado.web.RequestHandler):

	def initialize(self):
			self.db = self.settings["db"]
			self.template_collection = self.db[template_collection_name]
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
			template_id = self.request.arguments.get("template_id")[0].decode("utf-8")
		except Exception:
			template_id= None
		try:
			search_text = self.request.arguments.get("search_text")[0].decode("utf-8")
		except Exception:
			search_text = None

		user = yield self.user_collection.find_one({"user_id": user_id})

		
		templates = []
		if search_text:
				template_count = yield self.template_collection.find({ 
							"$text":{"$search": search_text}}, projection={"_id": False, "ngrams": False, "template": False}).count()
				
				pprint ("This is the template count %s"%template_count)
				cursor = self.template_collection.find({
							"$text":{"$search": search_text}}, projection={"_id": False, "ngrams": False, "template": False}).skip(skip).limit(limit)
				while (yield cursor.fetch_next):
					templates.append(cursor.next_object())
			
		else:
				template_count = yield self.template_collection.find(projection={"_id": False, "ngrams": False}).count()
				cursor = self.template_collection.find(projection={"_id": False, "ngrams": False, "template": False}).skip(skip).limit(limit)
				while (yield cursor.fetch_next):
					templates.append(cursor.next_object())

		template_ids = []
		for module in templates:
			template_ids.append(module.get("template_id"))

		message = {"error": True, "success": False, "message": "Success", "data": {"templates": templates, "template_ids": template_ids, 
						"module_count": template_count, "pages": math.ceil(template_count/limit)}}

		pprint (message)
		self.write(message)
		self.finish()
		return

	@staticmethod
	@tornado.gen.coroutine
	def get_children(module, db, child_collection_name):
		module_id = module["id"]

		children = []
		cursor = db[child_collection_name].find({"parent_id": module_id}, projection={"_id": False, "module_id": True, "module_name": True,  "child_collection_name": True })
		while (yield cursor.fetch_next):
			children.append(cursor.next_object())

		for child in children:
			name = child.pop("module_name")
			_id = child.pop("module_id")
			child.update({"name": name, "id": _id})


		if children:
			for child in children:
				if child.get("child_collection_name"):
					__child_collection_name = child.pop("child_collection_name")
					__children = yield Templates.get_children(child, db, __child_collection_name)
					child.update({"children": __children})

				else:
					child.pop("child_collection_name")
					
			return children
		else:
			return []


	@staticmethod
	@tornado.gen.coroutine
	def modify_children(module):
		children = module["children"]
		if children:
			for child in module["children"]:
				if child.get("children"):
					name = child.pop("module_name")
					_id = child.pop("module_id")
					child.pop("child_collection_name")
					child = {"name": name, "id": _id, "children": child.get("children")}
					__children = yield Templates.modify_children(child)
					child.update({"children": __children})
			return children
		else:
			return []


	@cors
	@tornado.web.asynchronous
	@tornado.gen.coroutine
	def  delete(self):
		user_id = self.request.arguments.get("user_id")[0].decode("utf-8")
		template_id = self.request.arguments.get("template_id")[0].decode("utf-8")
		try:
			#post_arguments = json.loads(self.request.body.decode("utf-8"))
			#user_id = post_arguments.get("user_id", None) ##who created this category
			if not template_id:
				raise Exception("Please send the template id")
		
			template = yield self.template_collection.find_one({"module_id": template_id})
			user = yield self.user_collection.find_one({"user_id": user_id})
			if user["user_type"] == "superadmin":
				yield self.template_collection.delete_one({"template_id": template_id})
			else:
				raise Exception("You have insufficient permissions to delete this module")
		except Exception as e:
			print (e)
			self.set_status(403)
			self.write(str(e))
			self.finish()
			return 


		self.write({"data": template_id})
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
		template_name = post_arguments.get("template_name")
		description = post_arguments.get("description")
		board = post_arguments.get("board")
		_class = post_arguments.get("class")
		template = post_arguments.get("template")

		
		#user = yield db[credentials].find_one({'user_type': user_type, "username": username, "password": password})
		
		try:
			if not template_name or not template:
				raise Exception("Template Name or Template itself is missing")


			template_object = yield self.template_collection.find_one({"template_name": template_name}, projection={"_id": False, "template_name": True})
			if template_object:
				raise Exception("Template has already been made, Please select a diffrent name for the template")

			_id = str(uuid.uuid4())

			template_object = {"template_id": _id, "template_name": template_name,  "utc_epoch": time.time(), "description": description,
									"indian_time": indian_time(), "ngrams": " ".join(make_ngrams(template_name)),
									"board": board, "class": _class, "template": template 
			}
			yield self.template_collection.insert_one(template_object)
		
		except Exception as e:
				logger.error(e)
				self.set_status(401)
				self.write(e.__str__())
				#self.write({"error": False, "success": True})
				self.finish()
				return 

		template_object.pop("_id")
		template_object.pop("template")
		message = {"error": False, "success": True, "data": {"template": template_object, "template_id": template_object["template_id"]}}
		pprint (message)
		self.write(message)
		self.finish()
		return 


