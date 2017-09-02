
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
    def get_permission_rest_parameter(user, module, rest_parameter, permission_collection):


        if user["user_type"] in ["superadmin"]:
            return True

        ##If the creator of themodule is user him/herself.
        if user["user_id"] == module["user_id"]:
            return True

        permission = yield permission_collection.find_one({"user_id": user["user_id"], 
											"module_id": module["module_id"]})
        return permission["permission"][rest_parameter]


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
    def get_modules(user, parent_id, skip, limit, module_type, textsearch, module_collection, permission_collection):
        ##If a user is superadmin, he will get eveything, If a user is admin he will get all the modules
        ## and a permission object in which it will be specified which permission he have on module
        ## if a user is normal user, a query will be done on permission_collection to find all the modules
        ## with user_id, As no permission with get can exist on user_id, We are assuming that all the 
        ## entries on permission_collection with this user_id must already have get permisisons
        
        
        
        modules = []
        if user["user_type"] == "admin":
            if textsearch:
                cursor = module_collection.find({"parent_id": parent_id, "creation_approval": True, "deletion_approval": False,
                "$text":{"$search": textsearch}}, projection={"_id": False, "ngrams": False}).skip(skip).limit(limit)
            
            else:
                module_count = yield module_collection.find({"parent_id": parent_id, "creation_approval": True, "deletion_approval": False}).count()
                cursor = module_collection.find({"parent_id": parent_id, "creation_approval": True, "deletion_approval": False},
                             projection={"_id": False, "ngrams": False}).skip(skip).limit(limit)
            while (yield cursor.fetch_next):
                modules.append(cursor.next_object())
            
            result = []
            for module in modules:
                permission = yield Permissions.get_permissions(user, module, permission_collection)
                if permission:
                    permission = permission
                else:
                    permission = {"get": True, "edit": False, "delete": False, "add_child": False}
                module.update({"permission": permission})
                result.append(module)
            return (result, module_count)
        else:
            cursor =  permission_collection.find({"user_id": user["user_id"], "parent_id": parent_id, 
                                                        "module_type": module_type}, projection={"_id": False, "ngrams": False}).skip(skip).limit(limit)
            module_count =  yield permission_collection.find({"user_id": user["user_id"], "parent_id": parent_id, 
                                                        "module_type": module_type}).count()

            while (yield cursor.fetch_next):
                modules.append(cursor.next_object())
            
            prin
            t (parent_id)
            print (user["user_id"])
            print (modules)
            result = []
            for permission in modules:
                module = yield module_collection.find_one({"module_id": permission.get("module_id"), "creation_approval": True, "deletion_approval": False}, 
                                                        projection={"_id": False})
                if module:
                    module.update({"permission": permission["permission"]})
                    result.append(module)
            return (modules, module_count)
        


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
    def set_permission_rest_paramter(user, module, parent, granter, rest_parameter, permission_collection):
        try:
                permissions = yield permission_collection.find_one({"user_id": user["user_id"], 
											"module_id": module["module_id"],
                                            "module_name": module["module_name"],
                                            "module_type": module["module_type"]}) 
        except Exception as e:
            print ("potties nikal gayii dude")
            print (e)
        print (permissions)
        print (rest_parameter)
        if not parent:
            parent_id = None

        if not permissions:
                per = {"get": False, "delete": False, "add_child": False, "edit": False}
                per.update({rest_parameter: True})

                print ("\n")
                print (per)
                print ("\n")
                yield permission_collection.update_one({"user_id": user["user_id"], 
											"module_id": module["module_id"],
                                            "module_name": module["module_name"],
                                            "module_type": module["module_type"], 
                                            "parent_id": parent_id,
											"granter_id": granter["user_id"]}, 
											{"$set": {"permission": per}}, 
                                            upsert=True)
                return


        yield permission_collection.update_one({"user_id": user["user_id"], 
											"module_id": module["module_id"],
                                            "module_name": module["module_name"],
                                            "module_type": module["module_type"], 
                                            "parent": parent,
											"granter_id": granter["user_id"]}, 
											{"$set": {"permission.%s"%rest_parameter: True}}, 
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
    def delete_user(user, module, permission_collection):
        yield permission_collection.delete_many({"user_id": user["user_id"]})
        return 



    @staticmethod
    @coroutine
    def set_permission_from_obj(user, module, permission_object, parent_id, 
					granter_id, permission_collection):
        try:
                permissions = yield permission_collection.find_one({"user_id": user["user_id"], 
											"module_id": module["module_id"],
                                            "module_name": module["module_name"],
                                            "module_type": module["module_type"]}) 
        except Exception as e:
            print ("potties nikal gayii dude")
            print (e)
        if not permissions:
                print ("Setting permisisons")
                result = yield permission_collection.update_one({"user_id": user["user_id"], 
											"module_id": module["module_id"], 
											"module_name": module["module_name"],
											"module_type": module["module_type"], 
											"parent_id": parent_id,
                                            "username": user["username"],
                                            "user_type": user["user_type"],
											"granter_id": granter_id}, 
											{"$set": {"permission": permission_object}}, upsert=True)

        else:
            print (permissions)
            print (permission_object)
            ##The granter_id cant be present because the previous granter may be different
            result = yield permission_collection.update_one({"user_id": user["user_id"], 
											"module_id": module["module_id"], 
											"module_name": module["module_name"],
											"module_type": module["module_type"], 
											"parent_id": parent_id,
											}, 
											{"$set": {"permission": permission_object}}, upsert=False)


            permissions = yield permission_collection.find_one({"user_id": user["user_id"], 
											"module_id": module["module_id"],
                                            "module_name": module["module_name"],
                                            "module_type": module["module_type"]}) 
            
            print (permissions)

        return result






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
    def is_not_domain(user, parent_module, module_type, permission_collection):   
	    # This implies that if a user wants to create a module other than domiain and if she is not 
        # superadmin or admin, then the create_child permission must be checked for the user.
        # if permission doesnt exists, it will raise an error 
        # If the module is to be created is not domain, then it must have a parent id
        if user["user_type"] == "superadmin":
            return True

        if not parent_module:
            raise Exception("Please provide a parent_id to create %s"%module_type)
        
        result = yield permission_collection.find_one({"user_id": user["user_id"], "module_id": parent_module["module_id"]})

        
        if not result or not result["permission"]["add_child"]:
            raise Exception("You dont have the required permissions to create children on  %s"%parent_module["module_name"])

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

