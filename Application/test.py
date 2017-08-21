#!/usr/bin/env python
#-*- coding: utf-8 -*-

import pymongo
import requests
import json
from faker import Faker
from pprint import pprint
import random
fake = Faker()
from LoggingModule.logging import logger
from termcolor import colored, cprint



app_port = 8000
mongo_user = "application"
mongo_pwd = "1234Pacific###"
mongo_ip = "localhost"
mongo_port = 27017
mongo_db_name = "dashboard"
user_collection_name = "users"


permission_collection_name = "permissions"


subject_collection_name = "subjects"
board_collection_name = "boards"
domain_collection_name = "domains"
concept_collection_name = "concepts"
subconcept_collection_name = "subconcepts"
nanoskill_collection_name = "nanoskills"
question_collection_name = "questions"
action_collection_name = "actions"

jwt_secret = "HelloOfAkind###"
app_super_admin = "nctsuperadmin"
app_super_admin_pwd = "1234Pacific###"
app_super_admin_user_id = "nctsuperadmin###"


##change this if you want all get requests for list to return more than 10 results
default_document_limit = 10

#uri = "mongodb://user:pass@localhost:27017/database_name"
uri = "mongodb://%s:%s@%s:%s/%s"%(mongo_user, mongo_pwd, mongo_ip, mongo_port, "admin")

connection = pymongo.MongoClient(uri)
db = connection[mongo_db_name]
users = db[user_collection_name]
domains = db[domain_collection_name]
concepts = db[concept_collection_name]
permissions = db[permission_collection_name]

logger.error("Deleting all collections to start a fresh run")
logger.error(users.remove())
logger.error(domains.remove())
logger.error(concepts.remove())
logger.error(permissions.remove())
logger.error("Checking api for users")


logger.error("creating first user as superadmin but it must fail as user_secret is not provided and must lies with superadmin")
r = requests.post("http://localhost:8000/users", data=json.dumps({"first_name": fake.first_name(), "last_name": fake.last_name(),\
 							"phone_number": fake.phone_number(), "email": fake.email(), "password": fake.password(),\
							 "user_type": "superadmin", "create_domain": True, "user_secret": "dsdsdsdssd", "username": fake.user_name()}))
print(colored(r.json(), "red"))

logger.error("creating first user as superadmin")
r1 = requests.post("http://localhost:8000/users", data=json.dumps({"first_name": fake.first_name(), "last_name": fake.last_name(),\
 							"phone_number": fake.phone_number(), "email": fake.email(), "password": fake.password(),\
							 "user_type": "superadmin", "create_domain": True, "user_secret": jwt_secret,"username": fake.user_name() }))
pprint(r1.json()["data"])

logger.error("creating first user as admin")
r2 = requests.post("http://localhost:8000/users", data=json.dumps({"first_name": fake.first_name(), "last_name": fake.last_name(),\
 							"phone_number": fake.phone_number(), "email": fake.email(), "password": fake.password(),\
							 "user_type": "admin", "create_domain": True, "user_secret": jwt_secret, "username": fake.user_name()}))
pprint(r2.json()["data"])

logger.error("creating first user as user_type=None, and he dosent have create_domain permissions")
r3 = requests.post("http://localhost:8000/users", data=json.dumps({"first_name": fake.first_name(), "last_name": fake.last_name(),\
 							"phone_number": fake.phone_number(), "email": fake.email(), "password": fake.password(),\
							 "user_type": None, "create_domain": False, "user_secret": jwt_secret, "username": fake.user_name()}))
pprint(r3.json()["data"])

logger.error("creating second user as user_type=None, and he have create_domain permissions")
r4 = requests.post("http://localhost:8000/users", data=json.dumps({"first_name": fake.first_name(), "last_name": fake.last_name(),\
 							"phone_number": fake.phone_number(), "email": fake.email(), "password": fake.password(),\
							 "user_type": None, "create_domain": True, "user_secret": jwt_secret, "username": fake.user_name()}))
pprint(r4.json()["data"])


logger.error("creating third user as user_type=None, and he doesnt have create_domain permissions")
r5 = requests.post("http://localhost:8000/users", data=json.dumps({"first_name": fake.first_name(), "last_name": fake.last_name(),\
 							"phone_number": fake.phone_number(), "email": fake.email(), "password": fake.password(),\
							 "user_type": None, "create_domain": False, "user_secret": jwt_secret, "username": fake.user_name()}))
pprint(r5.json()["data"])



users = {"superadmin": r1.json()["data"], "admin": r2.json()["data"], "user_one": r3.json()["data"], "user_two": r4.json()["data"], "user_three":r5.json()["data"] }

pprint (users)


##Create three domains, one by superadmin, it will have creation_approval on the creation but not visible to other users once superadmin provide permissions of it for
##other users, its name is superadmin_domain

## Create another domain by admin, it needs ot be approved by superadmin untill then it will not be visible to anyone except creator itself.

##user_one will try to create a domain but he copuldnt as his create_domain permission is False.
##user_two  will  create a domain but needs approval from the Superadmin.

r1 = requests.post("http://localhost:8000/domains", data=json.dumps({"module_name": "domain-%s"%fake.name(), "description": fake.text(), "user_id": users["superadmin"]["user_id"]}))
pprint (r1.json())
assert isinstance(r1.json()["data"], dict)
r2 = requests.post("http://localhost:8000/domains", data=json.dumps({"module_name": "domain-%s"%fake.name(), "description": fake.text(), "user_id": users["admin"]["user_id"]}))
pprint (r2.json())
assert isinstance(r2.json()["data"], dict)

logger.error("This user should be able to create domain as he doesnt have create_domain permissions on it")
r3 = requests.post("http://localhost:8000/domains", data=json.dumps({"module_name": "domain-%s"%fake.name(), "description": fake.text(), "user_id": users["user_one"]["user_id"]}))
pprint (r3.json())
assert isinstance(r3.json()["data"], str)



r4 = requests.post("http://localhost:8000/domains", data=json.dumps({"module_name": "domain-%s"%fake.name(), "description": fake.text(), "user_id": users["user_two"]["user_id"]}))
pprint (r4.json())
assert isinstance(r4.json()["data"], dict)

domains = {"superadmin_domain": r1.json()["data"], "admin_domain": r2.json()["data"], "user_two_domain": r4.json()["data"]}

############                       Checking Get permissions                 ########

##logger.error("checking get permissions")
logger.error("Superadmin will get all domains irresctive of their creation_approval and deletion_approval flags")
r1 = requests.get("http://localhost:8000/domains",data =json.dumps({"user_id": users["superadmin"]["user_id"]}))
pprint(r1.json())

##logger.error("admin will get all domains but only those whose creation_approval== True, which is only one domain created by superadmin")
r = requests.get("http://localhost:8000/domains", data =json.dumps({"user_id": users["admin"]["user_id"]}))
cprint(r.json()["data"]["module_ids"], "green")
assert r.json()["data"]["modules"][0]["module_id"] == domains["superadmin_domain"]["module_id"]

##logger.error("other users will get domains whose creation_approval== True and they have get permissions on it, the user who created the domain will only have get and edit permissions on it")
r = requests.get("http://localhost:8000/domains",data =json.dumps({"user_id": users["user_one"]["user_id"]}))
cprint ("The domain list shall be empty, as superadmin havent provided any permission to this user on any domain yet", "blue")
cprint(r.json()["data"])
assert r.json()["data"] == []


logger.info("Now first we will first try to pass the creation_approval flag from admin and other users")
logger.error("Put request by admin to change create_approval flag of the domain")
r = requests.put("http://localhost:8000/domains/%s"%domains["admin_domain"]["module_id"], data =json.dumps({"user_id": users["user_one"]["user_id"], "creation_approval": True }))
cprint(r.json()["data"], "green")
assert r.json()["data"] == "Only superadmin can change creation approval status"


##By default every module created by any user other then the superadmin needs an approval, needs to set creation_approval flag by superadmin
##Only then it will be visible to any other user.
logger.error("Changing creation_approval by ssuperadmin")
r = requests.put("http://localhost:8000/domains/%s"%domains["admin_domain"]["module_id"], data =json.dumps({"user_id": users["superadmin"]["user_id"], "creation_approval": True }))
message = "domain with %s has been updated"%(domains["admin_domain"]["module_id"])
cprint (message, "green")
cprint (r.json()["data"], "green")
assert r.json()["data"] == message

logger.error("Now checking if admin is getting two domains instead of one, as one other domain has been approved by superadmin")
r = requests.get("http://localhost:8000/domains", data =json.dumps({"user_id": users["admin"]["user_id"]}))
cprint(r.json()["data"]["module_ids"], "green")


logger.error("Now checking if user_two is getting his domain, he will get it even if its pending approval")
r = requests.get("http://localhost:8000/domains", data =json.dumps({"user_id": users["user_two"]["user_id"]}))
pprint(r.json())

logger.error("User one will not see any domain as he doesnt have any permission on any domain neither he created one")
r = requests.get("http://localhost:8000/domains", data =json.dumps({"user_id": users["user_one"]["user_id"]}))
pprint(r.json()["data"])




############                       Checking Get permissions after permission allotment                ########

##First lets try to give permission to domain by user_one to user_three, he would succeed as user_one doesnt have any permission on superadmin_domain
r = requests.put("http://localhost:8000/domains/%s"%domains["user_two_domain"]["module_id"],
				 data =json.dumps({"user_id": users["user_one"]["user_id"], "granter_id": users["user_two"]["user_id"], 
				  "permission": {"edit": True, "delete": False, "add_child": True, "get": True} }))
print(r.json())

##Now user_two has edit permission on one domain which he created
r = requests.put("http://localhost:8000/domains/%s"%domains["user_two_domain"]["module_id"],
				 data =json.dumps({"user_id": users["user_one"]["user_id"], "granter_id": users["user_two"]["user_id"], 
				  "permission": {"edit": True, "delete": False, "add_child": True, "get": True} }))
print(r.json())
# {'_id': ObjectId('599b126d4d7a7fafe55e154a'),
#  'edit': True,
#  'get': True,
#  'granter_id': '381749b586024ed849afbe7d78b0eaf505ba92b1',
#  'module_id': 'domain-50199c513e837c6b540285e2e94ce8fb9f02df69',
#  'module_name': 'domain-Thomas Walker',
#  'module_type': 'domain',
#  'parent_id': None,
#  'user_id': 'cdd99b010a8ec735446745c166ab2ea0abf0d156'}]
#This is the permission that will be added to the permission collcetion, for add_child: True it will raise an error, all other permissions will be added

#Trying to provide add_child permissions from superadmin to user_one 
## result will be that all the permissions will be added to this user_one like add_child now this user can create concepts
r = requests.put("http://localhost:8000/domains/%s"%domains["user_two_domain"]["module_id"],
				 data =json.dumps({"user_id": users["user_one"]["user_id"], "granter_id": users["superadmin"]["user_id"], 
				  "permission": {"edit": True, "delete": False, "add_child": True, "get": True} }))

print (r.json())







##MOre tests that needs to be added here are to check permissions and delete tests

###CONCEPTS

##this domain approval is stil pending so the superadmin is not alloed to create its children
r2 = requests.post("http://localhost:8000/concepts", data=json.dumps({"module_name": "concept-%s"%fake.name(), "parent_id": domains["user_two_domain"]["module_id"],\
														 "description": fake.text(), "user_id": users["superadmin"]["user_id"]}))


logger.error("Changing creation_approval by ssuperadmin")
r = requests.put("http://localhost:8000/domains/%s"%domains["user_two_domain"]["module_id"], data =json.dumps({"user_id": users["superadmin"]["user_id"], "creation_approval": True }))
message = "domain with %s has been updated"%(domains["admin_domain"]["module_id"])
cprint (r.json()["data"], "green")




r = requests.post("http://localhost:8000/concepts", data=json.dumps({"module_name": "concept-%s"%fake.name(), "parent_id": domains["user_two_domain"]["module_id"],\
														 "description": fake.text(), "user_id": users["superadmin"]["user_id"]}))

pprint (r.json()["data"])

r2 = requests.post("http://localhost:8000/concepts", data=json.dumps({"module_name": "concept-%s"%fake.name(), "parent_id": domains["user_two_domain"]["module_id"],\
														 "description": fake.text(), "user_id": users["superadmin"]["user_id"]}))
pprint (r.json()["data"])


r2 = requests.post("http://localhost:8000/concepts", data=json.dumps({"module_name": "concept-%s"%fake.name(), "parent_id": domains["user_two_domain"]["module_id"],\
														 "description": fake.text(), "user_id": users["superadmin"]["user_id"]}))
pprint (r.json()["data"])

##trying to create concepts by other users 
r = requests.post("http://localhost:8000/concepts", data=json.dumps({"module_name": "concept-%s"%fake.name(), "parent_id": domains["user_two_domain"]["module_id"],\
														 "description": fake.text(), "user_id": users["user_one"]["user_id"]}))
pprint (r.json()["data"])

r = requests.post("http://localhost:8000/concepts", data=json.dumps({"module_name": "concept-%s"%fake.name(), "parent_id": domains["user_two_domain"]["module_id"],\
														 "description": fake.text(), "user_id": users["user_two"]["user_id"]}))
pprint (r.json()["data"])

r = requests.post("http://localhost:8000/concepts", data=json.dumps({"module_name": "concept-%s"%fake.name(), "parent_id": domains["user_two_domain"]["module_id"],\
														 "description": fake.text(), "user_id": users["admin"]["user_id"]}))
pprint (r.json()["data"])



if __name__ == "__main__":
	pass



