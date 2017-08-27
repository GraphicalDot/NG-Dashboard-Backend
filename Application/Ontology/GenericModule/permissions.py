import tornado.options
import tornado.web
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
from delete_module import DeleteModule
class GenericPermissions(object):



    @staticmethod
	@coroutine
    def get_permissions(user, module, permission_collection):
        result = yield permission_collection.find_one({"user_id": user["user_id"], 
                "module_id": module["module_id"]}, projection={"_id": False, "permission": True})

        return result

    @staticmethod
	@coroutine
    def get_permission_get(user, module, permission_collection):


        if user["user_type"] in ["superadmin", "admin"]:
            return True

        ##If the creator of themodule is user him/herself.
        if user["user_id"] == module["user_id"]:
            return True

        permission = yield permission_collection.find_one({"user_id": user["user_id"], 
											"module_id": module["module_id"]}
        return permission["permission"]["get"]

    @staticmethod
	@coroutine
    def get_modules(user, skip, limit, textsearch, module_collection, permission_collection):
        ##If a user is superadmin, he will get eveything, If a user is admin he will get all the modules
        ## and a permission object in which it will be specified which permission he have on module
        ## if a user is normal user, a query will be done on permission_collection to find all the modules
        ## with user_id, As no permission with get can exist on user_id, We are assuming that all the 
        ## entries on permission_collection with this user_id must already have get permisisons
        if user["user_type"] == "admin":
            if textsearch:
                modules = yield module_collection.find({"user_id": user["user_id"], "creation_approval": True, "deletion_approval": False},
                {"module_name":{ "$text":{"$search": textsearch}}}).skip(skip).limit(limit)
            
            else:
                modules = yield module_collection.find({"user_id": user["user_id"]}).skip(skip).limit(limit)

            result = []
            for module in modules:
                permission = yield get_permissions(user, module, permission_collection)
                module.update({"permission": permission})
                result.append(module)
            return result
        else:
            modules =  yield permission_collection.find({"user_id": user["user_id"], 
                                                        "module_type": module_type})
            result = []
            for permission in modules:
                module = yield module_collection.find_one({"module_id": permission.get("module_id"), "creation_approval": True, "deletion_approval": False})
                if module:
                    module.update({"permission": permission})
                    result.append(module)
            return result
        




    @staticmethod
	@coroutine
    def get_permission_delete(user, module, permission_collection):
        if user["user_type"] == "superadmin":
            return True
        permission = yield permission_collection.find_one({"user_id": user["user_id"], 
											"module_id": module["module_id"]}
        return permission["permission"]["delete"]


    @staticmethod
	@coroutine
    def get_permission_addchild(user, module, permission_collection):
        
        if user["user_type"] == "superadmin":
            return True
        
        ##If the creator of themodule is user him/herself.
        if user["user_id"] == module["user_id"]:
            return True

        permission = yield permission_collection.find_one({"user_id": user["user_id"], 
											"module_id": module["module_id"]}
        return permission["permission"]["add_child"]

    @staticmethod
	@coroutine
    def get_permission_edit(user, module, permission_collection):
        if user["user_type"] in == "superadmin":
            return True

        ##If the creator of themodule is user him/herself.
        if user["user_id"] == module["user_id"]:
            return True


        permission = yield permission_collection.find_one({"user_id": user["user_id"], 
											"module_id": module["module_id"]}
        return permission["permission"]["edit"]




    @staticmethod
	@coroutine
    def set_permission_delete(user, module, parent, granter, permission_collection):
        get_permission = yield get_permission_get(user, module, permission_collection)
        if not get_permission:
            raise Exception ("This user must first be provided get permission on this object, as he will not be able to utilizie this permission")
        yield permission_collection.update_one({"user_id": user["user_id"], 
											"module_id": module["module_id"],
                                            "module_name": module["module_name"],
                                            "module_type": module["module_type"], 
                                            "parent": parent,
											"granter_id": granter["user_id"]}, 
											{"$set": {"permission.delete": True}}, 
                                            upsert=False)

		return 

    @staticmethod
    @coroutine
    def set_permission_get(user, module, parent, granter, permission_collection):
        yield permission_collection.update_one({"user_id": user["user_id"], 
											"module_id": module["module_id"], 
                                            "module_name": module["module_name"],
                                            "module_type": module["module_type"], 
                                            "parent": parent,
											"granter_id": granter["user_id"]}, 
											{"$set": {"permission.get": True}}, 
                                            upsert=False)

		return 

    @staticmethod
    @coroutine
    def set_permission_edit(user, module, parent, granter, permission_collection):
        get_permission = yield get_permission_get(user, module, permission_collection)
        if not get_permission:
            raise Exception ("This user must first be provided get permission on this object, as he will not be able to utilizie this permission")
        yield permission_collection.update_one({"user_id": user["user_id"], 
											"module_id": module["module_id"], 
                                            "module_name": module["module_name"],
                                            "module_type": module["module_type"], 
                                            "parent": parent,
											"granter_id": granter["user_id"]}, 
											{"$set": {"permission.edit": True}}, 
                                            upsert=False)

		return 

    @staticmethod
    @coroutine
    def set_permission_add_child(user, module, parent, granter,  permission_collection):
        get_permission = yield get_permission_get(user, module, permission_collection)
        if not get_permission:
            raise Exception ("This user must first be provided get permission on this object, as he will not be able to utilizie this permission")
        yield permission_collection.update_one({"user_id": user["user_id"], 
											"module_id": module["module_id"], 
                                            "module_name": module["module_name"],
                                            "module_type": module["module_type"], 
                                            "parent": parent,
											"granter_id": granter["user_id"]}, 
											{"$set": {"permission.add_child": True}}, 
                                            upsert=False)

		return 

    @coroutine
    def delete_permission_add_child(user, module, permission_collection):
        yield permission_collection.update_one({"user_id": user["user_id"], 
											"module_id": module["module_id"]}, 
											{"$set": {"permission.add_child": False}}, 
                                            upsert=False)

		return 


    @coroutine
    def delete_permission_get(user, module, permission_collection):
        yield permission_collection.update_one({"user_id": user["user_id"], 
											"module_id": module["module_id"]}, 
											{"$set": {"permission.get": False}}, 
                                            upsert=False)

		return 


    @coroutine
    def delete_permission_delete(user, module, permission_collection):
        yield permission_collection.update_one({"user_id": user["user_id"], 
											"module_id": module["module_id"]}, 
											{"$set": {"permission.delete": False}}, 
                                            upsert=False)
		return 

    @coroutine
    def delete_permission_edit(user, module, permission_collection):
        yield permission_collection.update_one({"user_id": user["user"], 
											"module_id": module["module"]}, 
											{"$set": {"permission.edit": False}}, 
                                            upsert=False)
		return 


    @coroutine
    def delete_user(user, module, permission_collection):
        yield permission_collection.delete_many({"user_id": user["user_id"]}) 
		return 



    @tornado.gen.coroutine
    def set_permission_from_obj(user, module, permission_object, parent_id, 
					granter_id, permission_collection):
		yield permission_collection.update_one({"user_id": user["user_id"], 
											"module_id": module["module_id"], 
											"module_name": module["module_name"],
											"module_type": module["module_type"], 
											"parent_id": parent_id,
											"granter_id": granter_id}, 
											{"$set": {"permission": permission_object}}, upsert=True)

		return 






    @staticmethod
    @tornado.gen.coroutine
    def is_domain(module_type, user):   
		if self.module_type == "domain":
			if user["user_type"] != "superadmin" or  not user["user_type"] != "admin":
				if not user["create_domain"]:
					raise Exception("The user who is trying to create this domain have insufficient permissions")
            return True
        return False

    @staticmethod
    @tornado.gen.coroutine
    def is_not_domain(user, module, permission_collection):   
	    # This implies that if a user wants to create a module other than domiain and if she is not 
        # superadmin or admin, then the create_child permission must be checked for the user.
        # if permission doesnt exists, it will raise an error 
        # If the module is to be created is not domain, then it must have a parent id
        if not parent_id:
			raise Exception("Please provide a parent_id to create %s"%self.module_type)
        
        result = get_permission_addchild(user, module, permission_collection)
        if not result:
                raise Exception("You dont have the required permissions to create children on  %s"%module["module_name"])

		return True


    @staticmethod
    @tornado.gen.coroutine
    def get_creation_approval(module):
        if module["creation_approval"]:
            return True
        return False


    @staticmethod
    @tornado.gen.coroutine
    def get_deletion_approval(module):
        if  module["deletion_approval"]:
            return True
        return False



    @staticmethod
    @tornado.gen.coroutine
    def set_creation_approval(module, module_collection):
        if module["creation_approval"]:
            raise Exception("The module with moduleid %s has already been approved"%module["module_id"])
        yield module_collection.update_one({"module_id": module["module_id"]}, {"$set": {"creation_approval": True}}, upsert=False)



    @staticmethod
    @tornado.gen.coroutine
    def set_deletion_approval(module, deletion_approval):
        yield module_collection.update_one({"module_id": module["module_id"]}, {"$set": {"deletion_approval": deletion_approval}}, upsert=False)
