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
	def o(module, child_collection_name):
		module_id = module["module_id"]
		children = db["child_collection_name"].find({"parent_id": module_id}, projection={"_id": False, "ngrams": False})
		for child in children:
			if child["child_collection_name"]:
				children = o(child, module["child_collection_name"])
				child.update({"childen": children})
		return children

		for module in db["domain_collection_name"].find(projection={"_id": False, "module_name": True, "module_id": True}):
			module



	@staticmethod
	@coroutine
	def delete_children(db, children, child_collection_name):
		child_collection = db[child_collection_name]
		for child in children:
			child = yield child_collection.find_one({"module_id": child["module_id"]})
			delete_id = yield child_collection.delete_one({"module_id": child["module_id"]})
			try:
				_child_collection_name = child["child_collection_name"]
				children = child["children"]
				if _child_collection_name:
					yield DeleteModule.delete_children(db, children, _child_collection_name)
			except Exception as e:
				logger.info(e)
				pass

		return False


	@staticmethod
	@coroutine
	def delete_module(db, module, module_collection, child_collection_name, parent_collection, permission_collection):
		children = module["children"]
		
		##deleteing module from the module collection
		yield module_collection.delete_one({"module_id": module["module_id"]})

		##DEleting all permissions for the module
		yield permission_collection.delete_many({"module_id": module["module_id"]})

		## Deleting child entry from the parent id as child_d is stroed in the parent under the array named as 
		## children
		if parent_collection:
				yield parent_collection.update_one({"module_id": module["parent_id"]}, {"$pull": {"children": {'module_id': module["module_id"],
				'module_name': module["module_name"]}}}, upsert=False)

		if child_collection_name:
		##deleting children one by one
			yield  DeleteModule.delete_children_permissions(db, children, child_collection_name, permission_collection)
			yield  DeleteModule.delete_children(db, children, child_collection_name)
		return 



	@staticmethod
	@coroutine
	def delete_children_permissions(db, children, child_collection_name, permission_collection):
		child_collection = db[child_collection_name]
		for child in children:
			child = yield child_collection.find_one({"module_id": child["module_id"]})
			delete_id = yield permission_collection.delete_many({"module_id": child["module_id"]})
			try:
				_child_collection_name = child["child_collection_name"]
				children = child["children"]
				if _child_collection_name:
					yield DeleteModule.delete_children_permissions(db, children, _child_collection_name, permission_collection)
			except Exception as e:
				logger.info(e)
				pass
		return False
		
	@staticmethod
	@coroutine
	def mark_module(db, module, module_collection, child_collection_name, parent_collection, permission_collection):
		children = module["children"]
		
		##deleteing module from the module collection
		yield module_collection.update_one({"module_id": module["module_id"]}, {"deletion_approval": True}, upsert=False)
		##deleting children one by one
		yield  DeleteModule.delete_children(db, children, child_collection_name)
		return 


	@staticmethod
	@coroutine
	def mark_children(db, children, child_collection_name):
		child_collection = db[child_collection_name]
		for child in children:
			child = yield child_collection.find_one({"module_id": child["module_id"]})
			delete_id = yield child_collection.update_one({"module_id": child["module_id"]}, {"deletion_approval": True}, upsert=False )
			try:
				_child_collection_name = child["child_collection_name"]
				children = child["children"]
				if _child_collection_name:
					yield DeleteModule.delete_children(db, children, _child_collection_name)
			except Exception as e:
				logger.info(e)
				pass

		return False


