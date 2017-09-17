import tornado.options
import tornado.web
from SettingsModule.settings import user_collection_name, domain_collection_name
from LoggingModule.logging import logger
from tornado.ioloop import IOLoop
import hashlib
import jwt
import json 
from pprint import pprint 

#https://emptysqua.re/blog/refactoring-tornado-coroutines/
## finding user from motor  yields a future object which is nothing but a promise that it will have a value in future
## and gen.coroutine is a perfect to resolve a future object uyntillit is resolved

from GeneralModule.cors import cors


class Templates(tornado.web.RequestHandler):

	def initialize(self):
			self.db = self.settings["db"]

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

		pprint (result)


		self.write({"error": False, "success": True, "data": result})
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
		username = post_arguments.get("username", None)
		password = post_arguments.get("password", None)

		
		#user = yield db[credentials].find_one({'user_type': user_type, "username": username, "password": password})
		
		try:
			if not username or not password:
				raise Exception("username and password must be given")


			user = yield self.collection.find_one({"username": username, "password": password}, projection={"_id": False, "phone_number": False, 
																				"permissions": False, "indian_time": False, "utc_epoch": False})
			if not user:
				raise Exception("user doesnt exist")
			token =  jwt.encode({'username': user["username"], "password": user["password"]}, jwt_secret, algorithm='HS256')
			user.update({"token": token.decode("utf-8")})
		
		except Exception as e:
				logger.error(e)
				self.set_status(401)
				pprint ({"error": True, "success": True, "token": None, "data": {"error": e.__str__()}})
				self.write( e.__str__())
				#self.write({"error": False, "success": True})
				self.finish()
				return 

		message = {"error": False, "success": True, "data": {"user": user, "token":token.decode("utf-8") }}
		pprint (message)
		self.write(message)
		self.finish()
		return 


