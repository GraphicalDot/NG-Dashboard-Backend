


#!/usr/bin/env python3
from SettingsModule.settings import question_collection_name, default_document_limit, indian_time
from tornado.web import asynchronous
from tornado.gen import coroutine
import tornado


class Question(tornado.web.RequestHandler):
	def initialize(self):
		self.db = self.settings["db"]
		self.collection = self.db[question_collection_name]	

	@asynchronous
	@coroutine
	def get(self, question_id):
			pass


	@asynchronous
	@coroutine
	def put(self, question_id):
			pass

	@asynchronous
	@coroutine
	def post(self, question_id):
			pass

	@asynchronous
	@coroutine
	def delete(self, question_id):
			pass



class Questions(tornado.web.RequestHandler):
	"""
	Return questions 
	Questions can filtered according to the 
		admin created id
		superadmin id
		category id
		sub category id
		date created	
	"""

	def initialize(self):
		self.db = self.settings["db"]
		self.collection = self.db[question_collection_name]	

	@asynchronous
	@coroutine
	def get(self, limit=None, skip=None, admin_id=None, category_id=None, sub_category_id=None, date_created=None):
		limit = self.get_argument("limit", None)
		skip = self.get_argument("skip", None)

		if not limit:
			limit = default_document_limit
		if not skip:
			skip = 0


		pass


