






from permissions import Permissions






class EditModule(object):


    def if_domain(module_type):


        ##Permissions
		##For the user other 
		
		#user = yield db[credentials].find_one({'user_type': user_type, "username": username, "password": password})
		
		try:
			if None in [module_name, description, user_id]:
				raise Exception("Fields shouldnt be empty")

			user = yield self.user_collection.find_one({"user_id": user_id})
			if not user:
				raise Exception("The user who is trying to create this domain doesnt exists")
				

			##if module type is domain then user either must be superadmin, admin or must have create_domain  permissions on the parent	
			if self.module_type == "domain":
				if user["user_type"] != "superadmin" or  not user["user_type"] != "admin":
					if not user["create_domain"]:
						raise Exception("The user who is trying to create this domain have insufficient permissions")
			
			## If module is not domain, A user must be superadmin, admin or have add_child perissions on the parent domain
			else:
				if not parent_id:
						raise Exception("Please provide a parent_id to create %s"%self.module_type)
				else:
					if user["user_type"] != "superadmin" or  not user["user_type"] != "admin":
						dummy = yield self.permission_collection.find_one({"module_id": parent_id, "user_id": user_id, "add_child": True})
						if not dummy:
								raise Exception("The user who is trying to create this %s have insufficient permissions"%self.module_type)
				
			##check if email is already registered with us
			module = yield self.module_collection.find_one({"module_name": module_name})
			if module:
				raise Exception("This module have already been created")

			_id = hashlib.sha1(module_name.encode("utf-8")).hexdigest()
			
			module_id = "%s-%s"%(self.module_type, _id)
			logger.info(module_id)
			if self.parent_collection:
					parent_document = yield self.parent_collection.find_one({"module_id": parent_id})

					if not parent_document:
						raise Exception("The parent id with id %s doesnt exists"%parent_id)
					##this is to ensure that child can only be made once its aproved by superadmin
					if not parent_document["creation_approval"] or parent_document["deletion_approval"] == "pending":
						raise Exception("Parent module creation first shall be approved by superadmin or its deletion is pending")

					parent_document["parents"].append({"module_id": parent_id,
																"module_name": parent_document["module_name"] })
					parents = parent_document["parents"]
					##This will add a children to the parent collection
					yield self.parent_collection.update({"module_id": parent_id}, {"$addToSet": \
								{"children": {"module_id": module_id, "module_name": module_name}}}, upsert=False)

			else:
				parents = []

			pprint (parents)
			##As this module is created by superadmin, it will not need any creation_approval approval
			if user["user_type"] == "superadmin":
				creation_approval = True
			else: 
				creation_approval = False
				

			#TODO
			#A permisssion check will be implemented here to check whether this user even have
			##the permission to make this object

			##deletion approval is False just after creation, If a user with delete permission wants to delete this module, 
			## It will be subjected to approval by superadmin, he can approve or disapprove its deletion, 
			## when a user submits its request to delete certain module, its status becomes pending
			module = {'module_name': "%s-%s"%(self.module_type, module_name), "description": description, "parent_id": parent_id, "parents": parents,
							 "module_id": module_id, "utc_epoch": time.time(), "indian_time": indian_time(), "username": user["username"],
							 "user_id": user_id, "status": True, "deletion_approval": False, "creation_approval": creation_approval, 
							  "module_type": self.module_type, "child_collection_name": self.child_collection_name, "children": []}
			yield self.module_collection.insert_one(module)

			pprint (module)
			

			logger.info("%s created at %s with module_id %s"%(self.module_type, indian_time(), module_id))
			
			if user["user_type"] != "superadmin":
				yield add_permission(user_id, module_id, module_name, self.module_type,
								 {"edit": True, "delete": False, "add_child": False, "get": True}, 
								 parent_id, user_id, self.permission_collection)
			
			
		

			#TODO: will be used to send email to the user
			##executor.submit(task, datetime.datetime.now())
		except Exception as e:
				logger.error(e)
				self.set_status(400)
				self.write({"error": True, "success": False, "token": None, "data": e.__str__()})
				self.finish()
				return 

		##This line has to be added, somehow while inserting nanoskill into the mongo, nanoskill itself got a new _id key
		##which is not serializable
		##TODO : implement JWT tokens
		module.pop("_id")
		self.write({"error": False, "success": True, "data": module})
		self.finish()
		return 


