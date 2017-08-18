#!/usr/bin env python     
from SettingsModule.settings  import user_collection_name, indian_time, jwt_secret, user_collection_name,\
                     usr_domain_permissions, usr_concept_permissions, usr_subconcept_permissions, usr_nanoskill_permissions, \
                     usr_question_permissions, domain_permissions, concepts_permissions, subconcepts_permissions, \
                    nanoskill_permissions, question_permissions, subject_collection_name, board_collection_name, \
                    domain_collection_name, concept_collection_name, subconcept_collection_name, 
                    nanoskill_collection_name
 
db = 

from LoggingModule.logging import logger
import time 
import hashlib
from pprint import pprint
import jwt
import json
from AuthenticationModule.authentication import auth
#https://emptysqua.re/blog/refactoring-tornado-coroutines/
## finding user from motor  yields a future object which is nothing but a promise that it will have a value in future
## and gen.coroutine is a perfect to resolve a future object uyntillit is resolved

import codecs

from generic.cors import cors
reader = codecs.getreader("utf-8")




"""
Permission os a user on any object may be of type read write and delete

"""


class UserPermissions(object):
        


        def user_domain_vailidty(user_id, object_id, object_type):
            """
            This method will check whether the user and the object exists or not
            """
            user = db["user_collection_name"].find_one({"user_id": user_id}, projection={"_id": False})
            domain = db["domain_collection_name"].find_one({"object_id": user_id}, projection={"_id": False})
            object_dictionary = {
                "domain": domain_collection_name, 
                "concept": concept_collection_name, 
                "subconcept": subconcept_collection_name, 
                "nanoskill": nanoskill_collection_name, 
                "question": question_collcetion_name
            }

            if not user and not domain:
                    raise Exception("Either User or Domainn doesnt Exists")



        def domain_check_permission():
            """
            this method checks if the user even have the permission to do the required
            action on the object
            """


        def domain_permission_add():
            

        def domain_permission_delete():


        def concept_permission_add();

        def concept_permission_delete();



        def subconcept_permission_add();

        def subconcept_permission_delete();



        def nanoskill_permission_add():

        def nanoskill_permission_delete():


        def question_permission_add():

        def question_permission_delete():
