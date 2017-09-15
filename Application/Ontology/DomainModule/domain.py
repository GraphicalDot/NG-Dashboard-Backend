import tornado.options
import tornado.web
from tornado.escape import json_decode as TornadoJsonDecode
from SettingsModule.settings  import domain_collection_name, indian_time, jwt_secret, \
									 default_document_limit, user_collection_name,\
									 permission_collection_name, concept_collection_name
from LoggingModule.logging import logger
import time 
import hashlib
import jwt
import json
from AuthenticationModule.authentication import auth
from Ontology.GenericModule.generic  import GenericPermissions, Generic
#https://emptysqua.re/blog/refactoring-tornado-coroutines/
## finding user from motor  yields a future object which is nothing but a promise that it will have a value in future
## and gen.coroutine is a perfect to resolve a future object uyntillit is resolved

import codecs
from GeneralModule.cors import cors
reader = codecs.getreader("utf-8")





class DomainPermissions(GenericPermissions):

	def initialize(self):
		self.db = self.settings["db"]
		self.parent_collection = None
		self.parent_name = None
		self.module_collection = self.db[domain_collection_name]
		self.user_collection = self.db[user_collection_name]
		self.module_type = "domain"
		self.child_collection = self.db[concept_collection_name]
		self.child_collection_name = concept_collection_name
		self.permission_collection = self.db[permission_collection_name]



class Domains(Generic):
	def initialize(self):
		self.db = self.settings["db"]
		self.parent_collection = None
		self.parent_name = None
		self.module_collection = self.db[domain_collection_name]
		self.user_collection = self.db[user_collection_name]
		self.module_type = "domain"
		self.child_collection = self.db[concept_collection_name]
		self.child_collection_name = concept_collection_name
		self.permission_collection = self.db[permission_collection_name]
		