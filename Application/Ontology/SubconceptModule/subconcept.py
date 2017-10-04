import tornado.options
import tornado.web
from tornado.escape import json_decode as TornadoJsonDecode
from SettingsModule.settings  import concept_collection_name, indian_time, jwt_secret, \
									 default_document_limit, domain_collection_name, \
									permission_collection_name, user_collection_name,\
									subconcept_collection_name, nanoskill_collection_name
from LoggingModule.logging import logger
import time 
import hashlib
from pprint import pprint
import jwt
import json
from AuthenticationModule.authentication import auth
from Ontology.GenericModule.generic import GenericPermissions, Generic, Allmodules
#https://emptysqua.re/blog/refactoring-tornado-coroutines/
## finding user from motor  yields a future object which is nothing but a promise that it will have a value in future
## and gen.coroutine is a perfect to resolve a future object uyntillit is resolved

import codecs

reader = codecs.getreader("utf-8")







class SubconceptPermissions(GenericPermissions):

	def initialize(self):
		self.db = self.settings["db"]
		self.parent_collection = self.db[concept_collection_name]
		self.parent_name = "concept"
		self.module_collection = self.db[subconcept_collection_name]
		self.user_collection = self.db[user_collection_name]
		self.module_type = "subconcept"
		self.child_collection = self.db[nanoskill_collection_name]
		self.child_collection_name = nanoskill_collection_name
		self.permission_collection = self.db[permission_collection_name]



class Subconcepts(Generic):
	def initialize(self):
		self.db = self.settings["db"]
		self.parent_collection = self.db[concept_collection_name]
		self.parent_name = "concept"
		self.module_collection = self.db[subconcept_collection_name]
		self.user_collection = self.db[user_collection_name]
		self.module_type = "subconcept"
		self.child_collection = self.db[nanoskill_collection_name]
		self.child_collection_name = nanoskill_collection_name
		self.permission_collection = self.db[permission_collection_name]
		

class Allsubconcepts(Allmodules):
	def initialize(self):
		self.db = self.settings["db"]
		self.parent_collection = self.db[concept_collection_name]
		self.parent_name = "concept"
		self.module_collection = self.db[subconcept_collection_name]
		self.user_collection = self.db[user_collection_name]
		self.module_type = "subconcept"
		self.child_collection = self.db[nanoskill_collection_name]
		self.child_collection_name = nanoskill_collection_name
		self.permission_collection = self.db[permission_collection_name]
