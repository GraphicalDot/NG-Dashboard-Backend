import tornado.options
import tornado.web
from SettingsModule.settings import credential_collection_name
from LoggingModule.logging import logger
from tornado.ioloop import IOLoop


#https://emptysqua.re/blog/refactoring-tornado-coroutines/
## finding user from motor  yields a future object which is nothing but a promise that it will have a value in future
## and gen.coroutine is a perfect to resolve a future object uyntillit is resolved
class Login(tornado.web.RequestHandler):

	def initialize(self):
			self.db = self.settings["db"]
			self.collection = self.db[credential_collection_name]

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
		user_type = self.get_argument("user_type", None)
		username = self.get_argument("username", None)
		password = self.get_argument("password", None)
		newpassword = self.get_argument("newpassword", None)
		logger.info("user_type=%s, username=%s, password=%s, newpassword=%s"%(user_type, username, password, newpassword))

		
		db = self.settings["db"]
		#user = yield db[credentials].find_one({'user_type': user_type, "username": username, "password": password})
		
		try:
			if not user_type:
				raise Exception("user_type cannot be left unattempted")

			if not username or not password:
				raise Exception("username and password must be given")


			user = yield self.collection.find_one({'user_type': user_type, "username": username, "password": password})
			if not user:
				raise Exception("user doesnt exist")
		
		except Exception as e:
				logger.error(e)
				self.write({"error": False, "success": True, "token": None, "message": e.__str__()})
				#self.write({"error": False, "success": True})
				self.finish()
				return 

		self.write({"error": False, "success": True, "token": "security"})
		self.finish()
		return 


