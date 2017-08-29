
#-*- coding: utf-8 -*-
import tornado.options
import tornado.web
from tornado.gen import coroutine
from tornado.escape import json_decode as TornadoJsonDecode

import time 
import hashlib
import jwt
import json
from .delete_module import DeleteModule

class Permissions(object):

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
											"module_id": module["module_id"]})
        return permission["permission"]["get"]


    @staticmethod
    @coroutine
    def get_permissions_modules(skip, limit, module, permission_collection, user_collection):
        ## Now when getting the permissions for module, superadmin wil not be present and also the admins
        ## who dont have any delete, edit and add_child permissions on it, because by default admin gets 
        ## only a get permission on the object
        module_permissions = []
        cursor = permission_collection.find({"module_id": module["module_id"]}, projection={"_id": False})
        while (yield cursor.fetch_next):
                module_permissions.append(cursor.next_object())

        admins_in_permissions = [_object["user_id"] for _object in module_permissions]

        superadmins = []
        cursor =  user_collection.find({"user_type": "superadmin"}, projection={"_id": False})
        while (yield cursor.fetch_next):
                superadmins.append(cursor.next_object())
        
        for user in superadmins:
                permission_object = {"get": True, "edit": True, "add_child": True, "delete": True}
                module_permissions.append({"user_id": user["user_id"], 
											"module_id": module["module_id"],
                                            "user_type": user["user_type"], 
											"module_name": module["module_name"],
											"module_type": module["module_type"], 
											"parent_id": module["parent_id"],
                                            "username": user["username"],
											"granter_id": None, 
											"permission": permission_object}
                                )
        admins = []
        cursor =  user_collection.find({"user_type": "admin"}, projection={"_id": False})
        while (yield cursor.fetch_next):
                admins.append(cursor.next_object())
        
        for user in admins:
            if user["user_id"] not in admins_in_permissions:
                permission_object = {"get": True, "edit": False, "add_child": False, "delete": False}
                module_permissions.append({"user_id": user["user_id"], 
											"module_id": module["module_id"],
                                            "user_type": user["user_type"], 
											"module_name": module["module_name"],
											"module_type": module["module_type"], 
											"parent_id": module["parent_id"],
                                            "username": user["username"],
											"granter_id": None, 
											"permission": permission_object}
                                )
        return module_permissions

    @staticmethod
    @coroutine
    def get_permissions_user(skip, limit, user, module_type, module_collection, permission_collection):
        
        print ("Get Permission user")
        modules = []
        cursor =  permission_collection.find({"user_id": user["user_id"], "module_type": module_type}, projection={"_id": False}).skip(skip).limit(limit)
        while (yield cursor.fetch_next):
            modules.append(cursor.next_object())

        if user["user_type"] == "admin":
            modules_in_permissions = [_object["module_id"] for _object in modules]
            print ("\n")
            print (modules_in_permissions)
            print ("\n")

            all_modules = []

            print (module_collection)
            cursor = module_collection.find({"module_type": module_type}, projection={"_id": False}).skip(skip).limit(limit)
            while (yield cursor.fetch_next):
                all_modules.append(cursor.next_object())

            for module in all_modules:
                if module["module_id"] not in modules_in_permissions:
                    permission_object = {"get": True, "edit": False, "add_child": False, "delete": False}
                    modules.append({"user_id": user["user_id"], 
											"module_id": module["module_id"],
                                            "user_type": user["user_type"], 
											"module_name": module["module_name"],
											"module_type": module["module_type"], 
											"parent_id": module["parent_id"],
                                            "username": user["username"],
											"granter_id": None, 
											"permission": permission_object}
                                )
        return modules


    @staticmethod
    @coroutine
    def get_modules(user, skip, limit, module_type, textsearch, module_collection, permission_collection):
        ##If a user is superadmin, he will get eveything, If a user is admin he will get all the modules
        ## and a permission object in which it will be specified which permission he have on module
        ## if a user is normal user, a query will be done on permission_collection to find all the modules
        ## with user_id, As no permission with get can exist on user_id, We are assuming that all the 
        ## entries on permission_collection with this user_id must already have get permisisons
        
        
        
        modules = []
        if user["user_type"] == "admin":
            if textsearch:
                cursor = yield module_collection.find({"creation_approval": True, "deletion_approval": False},
                {"module_name":{ "$text":{"$search": textsearch}}}, projection={"_id": False}).skip(skip).limit(limit)
            
            else:
                cursor = module_collection.find({"creation_approval": True, "deletion_approval": False} , projection={"_id": False}).skip(skip).limit(limit)
            while (yield cursor.fetch_next):
                modules.append(cursor.next_object())
            
            result = []
            for module in modules:
                permission = yield Permissions.get_permissions(user, module, permission_collection)
                if permission:
                    permission = permission
                else:
                    permission = {"get": True, "edit": True, "delete": False, "add_children": False}
                module.update({"permission": permission})
                result.append(module)
            return result
        else:
            cursor =  permission_collection.find({"user_id": user["user_id"], 
                                                        "module_type": module_type}, projection={"_id": False}).skip(skip).limit(limit)

            while (yield cursor.fetch_next):
                modules.append(cursor.next_object())
            
            result = []
            for permission in modules:
                module = yield module_collection.find_one({"module_id": permission.get("module_id"), "creation_approval": True, "deletion_approval": False}, 
                                                        projection={"_id": False})
                if module:
                    module.update({"permission": permission})
                    result.append(module)
            return result
        


    @staticmethod
    @coroutine
    def edit_permissions(user_id, granter_id, modules_object, permission_collection, domain_collection):
        """
        module_object = {"domains":  [{}], 
                        "concepts": [{}], 
                        "subconcepts": [{}, {}],
                        "nanoskill": [{}, {}, ...]} 

        """

        return 



    @staticmethod
    @coroutine
    def get_permission_delete(user, module, permission_collection):
        if user["user_type"] == "superadmin":
            return True
        permission = yield permission_collection.find_one({"user_id": user["user_id"], 
											"module_id": module["module_id"]})
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
											"module_id": module["module_id"]})
        return permission["permission"]["add_child"]

    @staticmethod
    @coroutine
    def get_permission_edit(user, module, permission_collection):
        if user["user_type"] == "superadmin":
            return True

        ##If the creator of themodule is user him/herself.
        if user["user_id"] == module["user_id"]:
            return True


        permission = yield permission_collection.find_one({"user_id": user["user_id"], 
											"module_id": module["module_id"]})
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


    @staticmethod
    @coroutine
    def delete_permission_add_child(user, module, permission_collection):
        yield permission_collection.update_one({"user_id": user["user_id"], 
											"module_id": module["module_id"]}, 
											{"$set": {"permission.add_child": False}}, 
                                            upsert=False)

        return 


    @staticmethod
    @coroutine
    def delete_permission_get(user, module, permission_collection):
        yield permission_collection.update_one({"user_id": user["user_id"], 
											"module_id": module["module_id"]}, 
											{"$set": {"permission.get": False}}, 
                                            upsert=False)

        return 


    @staticmethod
    @coroutine
    def delete_permission_delete(user, module, permission_collection):
        yield permission_collection.update_one({"user_id": user["user_id"], 
											"module_id": module["module_id"]}, 
											{"$set": {"permission.delete": False}}, 
                                            upsert=False)
        return 

    @staticmethod
    @coroutine
    def delete_permission_edit(user, module, permission_collection):
        yield permission_collection.update_one({"user_id": user["user"], 
											"module_id": module["module"]}, 
											{"$set": {"permission.edit": False}}, 
                                            upsert=False)
        return 

    @staticmethod
    @coroutine
    def delete_user(user, module, permission_collection):
        yield permission_collection.delete_many({"user_id": user["user_id"]})
        return 



    @staticmethod
    @coroutine
    def set_permission_from_obj(user, module, permission_object, parent_id, 
					granter_id, permission_collection):
        yield permission_collection.update_one({"user_id": user["user_id"], 
											"module_id": module["module_id"], 
											"module_name": module["module_name"],
											"module_type": module["module_type"], 
											"parent_id": parent_id,
                                            "username": user["username"],
                                            "user_type": user["user_type"],
											"granter_id": granter_id}, 
											{"$set": {"permission": permission_object}}, upsert=True)
        return 






    @staticmethod
    @tornado.gen.coroutine
    def is_domain(module_type, user):
        if module_type == "domain":
            print ("module_type is domain")
            if user["user_type"] != "superadmin" or  not user["user_type"] != "admin":
                if not user["create_domain"]:
                    raise Exception("The user who is trying to create this domain have insufficient permissions")
            print ("user have create_domain permissions")
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

