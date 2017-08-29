import tornado.options
from tornado.gen import coroutine
from tornado.escape import json_decode as TornadoJsonDecode
from SettingsModule.settings  import domain_collection_name, indian_time, jwt_secret, \
									 default_document_limit, user_collection_name, permission_collection_name, \
									 action_collection_name

from LoggingModule.logging import logger
import time 
import hashlib
import jwt
import json
from AuthenticationModule.authentication import auth



class DeleteModule(object):
	@staticmethod
	@coroutine
	def delete_module_n_children(db, module, module_collection, child_collection_name):
		module = yield module_collection.find({"module_id": module["module_id"]})
		children = module["children"]
		
		self.module_collection.delete_one({"module_id": module["module_id"]})
		collection = db[child_collection_name]
		for child in children:
			child = yield collection.find_one({"module_id": child["module_id"]})
			delete_id = yield collection.delete_one({"module_id": child["module_id"]})
			try:
				child_children = child["children"]
				child_child_collection_name = child["child_collection_name"]
				if child_child_collection_name:
					DeleteModule.delete_children(db, child_children, child_child_collection_name)
			except Exception as e:
				logger.info(e)
				pass

		return False




	@staticmethod
	@coroutine
	def delete_module_n_children_permissions(db, module, module_collection, child_collection_name, permission_collection):
		module = yield module_collection.find({"module_id": module["module_id"]})
		children = module["children"]
		
		self.permission_collection.delete_one({"module_id": module["module_id"]})
		collection = db[child_collection_name]
		for child in children:
			child = yield collection.find_one({"module_id": child["module_id"]})
			delete_id = yield permisision_collection.delete_one({"module_id": child["module_id"]})
			try:
				child_children = child["children"]
				child_child_collection_name = child["child_collection_name"]
				if child_child_collection_name:
					DeleteModule.delete_children(db, child_children, child_child_collection_name)
			except Exception as e:
				logger.info(e)
				pass

		return False



	@staticmethod
	@coroutine
	def mark_deletion(db, module, module_collection, child_collection_name, deletion_approval):
		module = yield module_collection.find({"module_id": module["module_id"]})
		children = module["children"]

		self.module_collection.update_one({"module_id": module["module_id"]}, {"deletion_approval": deletion_approval}, upsert=False)

		collection = db[child_collection_name]
		for child in children:
			child = yield collection.find_one({"module_id": child["module_id"]})
			delete_id = yield collection.update_one({"module_id": child["module_id"]}, {"deletion_approval": deletion_approval}, upsert=False)
			try:
				child_children = child["children"]
				child_child_collection_name = child["child_collection_name"]
				if child_child_collection_name:
					DeleteModule.delete_children(db, child_children, child_child_collection_name)
			except Exception as e:
				logger.info(e)
				pass

		return False
