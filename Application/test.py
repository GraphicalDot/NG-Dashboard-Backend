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
users_collection = db[user_collection_name]
domains = db[domain_collection_name]
concepts = db[concept_collection_name]
subconcepts = db[subconcept_collection_name]
nanoskills = db[nanoskill_collection_name]
questions = db[question_collection_name]
permissions = db[permission_collection_name]

logger.error("Deleting all collections to start a fresh run")
logger.error(users_collection.remove())
logger.error(domains.remove())
logger.error(concepts.remove())
logger.error(subconcepts.remove())
logger.error(nanoskills.remove())
logger.error(questions.remove())
logger.error(permissions.remove())
logger.error("Checking api for users")

USER_URL = "http://localhost:8000/users"
DOMAIN_URL = "http://localhost:8000/domains"
DOMAIN_PERMISSIONSURL = "http://localhost:8000/domainpermissions"
CONCEPT_URL = "http://localhost:8000/concepts"
SUBCONCEPT_URL = "http://localhost:8000/subconcepts"
NANO_URL = "http://localhost:8000/nanoskills"


logger.error("creating first user as superadmin but it must fail as user_secret is not provided and must lies with superadmin")
r = requests.post("http://localhost:8000/users", data=json.dumps({"first_name": fake.first_name(), "last_name": fake.last_name(),\
 							"phone_number": fake.phone_number(), "email": fake.email(), "password": fake.password(),\
							 "user_type": "superadmin", "create_domain": True, "user_secret": "dsdsdsdssd", "username": fake.user_name()}))
#print(colored(r.json(), "red"))

logger.error("creating first user as superadmin")
r1 = requests.post("http://localhost:8000/users", data=json.dumps({"first_name": fake.first_name(), "last_name": fake.last_name(),\
 							"phone_number": fake.phone_number(), "email": fake.email(), "password": fake.password(),\
							 "user_type": "superadmin", "create_domain": True, "user_secret": jwt_secret,"username": fake.user_name() }))
#pprint(r1.json()["data"])

logger.error("creating first user as admin")
r2 = requests.post("http://localhost:8000/users", data=json.dumps({"first_name": fake.first_name(), "last_name": fake.last_name(),\
 							"phone_number": fake.phone_number(), "email": fake.email(), "password": fake.password(),\
							 "user_type": "admin", "create_domain": True, "user_secret": jwt_secret, "username": fake.user_name()}))
#pprint(r2.json()["data"])

logger.error("creating first user as user_type=None, and he dosent have create_domain permissions")
r3 = requests.post("http://localhost:8000/users", data=json.dumps({"first_name": fake.first_name(), "last_name": fake.last_name(),\
 							"phone_number": fake.phone_number(), "email": fake.email(), "password": fake.password(),\
							 "user_type": None, "create_domain": False, "user_secret": jwt_secret, "username": fake.user_name()}))
#pprint(r3.json()["data"])

logger.error("creating second user as user_type=None, and he have create_domain permissions")
r4 = requests.post("http://localhost:8000/users", data=json.dumps({"first_name": fake.first_name(), "last_name": fake.last_name(),\
 							"phone_number": fake.phone_number(), "email": fake.email(), "password": fake.password(),\
							 "user_type": None, "create_domain": True, "user_secret": jwt_secret, "username": fake.user_name()}))
#pprint(r4.json()["data"])


logger.error("creating third user as user_type=None, and he doesnt have create_domain permissions")
r5 = requests.post("http://localhost:8000/users", data=json.dumps({"first_name": fake.first_name(), "last_name": fake.last_name(),\
 							"phone_number": fake.phone_number(), "email": fake.email(), "password": fake.password(),\
							 "user_type": None, "create_domain": False, "user_secret": jwt_secret, "username": fake.user_name()}))
#pprint(r5.json()["data"])



users = {"superadmin": r1.json()["data"], "admin": r2.json()["data"], "user_one": r3.json()["data"], "user_two": r4.json()["data"], "user_three":r5.json()["data"] }

f = users_collection.update({"user_id": users["superadmin"]["user_id"]}, {"$set": {"username": "q", "password": "q"}}, upsert=False)
#pprint (f)
pprint (users)

##Create three domains, one by superadmin, it will have creation_approval on the creation but not visible to other users once superadmin provide permissions of it for
##other users, its name is superadmin_domain

## Create another domain by admin, it needs ot be approved by superadmin untill then it will not be visible to anyone except creator itself.

##user_one will try to create a domain but he copuldnt as his create_domain permission is False.
##user_two  will  create a domain but needs approval from the Superadmin.


description = fake.text()
module_name = fake.name()
user_id = users["superadmin"]["user_id"]
r1 = requests.post(DOMAIN_URL, data=json.dumps({"module_name": module_name, "description": description, "user_id": user_id}))
if domains.find_one({"description": description, "user_id": user_id}, projection={"_id": False}):
		_str = "Creation of domain by super admin test".ljust(200) + "****Test Passed <<1>>***" + "\n"
		cprint(_str, "green")
else:
		_str = "Creation of domain by super admin test".ljust(200) + "****Test Failed***" + "\n"
		cprint(_str, "red")
	

for i in range(100):
	description = fake.text()
	module_name = fake.name()
	user_id = users["superadmin"]["user_id"]
	r1 = requests.post(DOMAIN_URL, data=json.dumps({"module_name": module_name, "description": description, "user_id": user_id}))
	



description = fake.text()
module_name = fake.name()
user_id = users["admin"]["user_id"]
r2 = requests.post(DOMAIN_URL, data=json.dumps({"module_name": module_name, "description": description, "user_id": user_id}))
if domains.find_one({"description": description, "user_id": user_id}, projection={"_id": False}):
		_str = "Creation of domain by admin test".ljust(200) + "****Test Passed <<2>>***" + "\n"
		cprint(_str, "green")
else:
		_str = "Creation of domain by admin test".ljust(200) + "****Test Failed***" + "\n"
		cprint(_str, "red")



description = fake.text()
module_name = fake.name()
user_id = users["user_one"]["user_id"]
r3 = requests.post(DOMAIN_URL, data=json.dumps({"module_name": module_name, "description": description, "user_id": user_id}))
if not domains.find_one({"description": description, "user_id": user_id}, projection={"_id": False}) and not r.json()["success"]:
		_str = "Creation of domain by user_one failed".ljust(200) + "****Test Passed <<3>>***" + "\n"
		cprint(_str, "green")
else:
		_str = "Creation of domain by user_one succeded".ljust(200) + "****Test Failed***" + "\n"
		cprint(_str, "red")


description = fake.text()
module_name = fake.name()
user_id = users["user_two"]["user_id"]
cprint("Create permission for this user %s"%users["user_two"]["create_domain"], "green")
r4 = requests.post(DOMAIN_URL, data=json.dumps({"module_name": module_name, "description": description, "user_id": user_id}))
if domains.find_one({"description": description, "user_id": user_id}, projection={"_id": False}) and r4.json()["success"]:
		_str = "Creation of domain by user_two succeded".ljust(200) + "****Test Passed <<4>>***" + "\n"
		cprint(_str, "green")
else:
		_str = "Creation of domain by user_two failed".ljust(200) + "****Test Failed***" + "\n"
		cprint(_str, "red")




domains_object = {"superadmin": r1.json()["data"], "admin": r2.json()["data"], "user_two": r4.json()["data"]}


############                       Checking Get permissions                 ########

##logger.error("checking get permissions")
r = requests.get(DOMAIN_URL, params={"user_id": users["superadmin"]["user_id"]})
if domains.count() == r.json()["data"]["module_count"]:
		_str = "Get request by superadmin on domain getting all the domains".ljust(200) + "****Test Passed <<5>>***" + "\n"
		cprint(_str, "green")
else:
		_str = "Creation of domain by user_two failed".ljust(200) + "****Test Failed***" + "\n"
		cprint(_str, "red")



##logger.error("admin will get all domains but only those whose creation_approval== True, which is only one domain created by superadmin")
r = requests.get(DOMAIN_URL, params ={"user_id": users["admin"]["user_id"]})
cprint ("As admin user will get every possible domain but only those whose creation_approval==True and deletion_approval=False", "green")
if domains.find({"creation_approval": True, "deletion_approval": False}).count() == r.json()["data"]["module_count"]:
		_str = "Get request by admin on domain getting all the domains with flags".ljust(200) + "****Test Passed <<6>>***" + "\n"
		cprint(_str, "green")
else:
		_str = "Creation of domain by user_two failed".ljust(200) + "****Test Failed***" + "\n"
		cprint(_str, "red")


##logger.error("other users will get domains whose creation_approval== True and they have get permissions on it, the user who created the domain will only have get and edit permissions on it")
r = requests.get(DOMAIN_URL, params={"user_id": users["user_one"]["user_id"]})
if len(r.json()["data"]["module_ids"]) == 0:
		_str = "Get request by user_one, He will not get any domains yet".ljust(200) + "****Test Passed  <<7>>***" + "\n"
		cprint(_str, "green")
else:
		_str = "Get request by user_one failed, as he didnt receive emppty list of domains".ljust(200) + "****Test Failed***" + "\n"
		cprint(_str, "red")


r = requests.get(DOMAIN_URL, params={"user_id": users["user_one"]["user_id"]})
if len(r.json()["data"]["module_ids"]) == 0:
		_str = "Get request by user_one, He will not get any domains yet".ljust(200) + "****Test Passed <<8>>***" + "\n"
		cprint(_str, "green")
else:
		_str = "Get request by user_one failed, as he didnt receive emppty list of domains".ljust(200) + "****Test Failed***" + "\n"
		cprint(_str, "red")


logger.info("Test")
r = requests.get(DOMAIN_URL, params={"user_id": users["user_two"]["user_id"]})
cprint ("Althogh user_two have created a domain, he will not get any as its not creation_approval by superadmin", "green")
if len(r.json()["data"]["module_ids"]) == 0:
		_str = "Get request by user_two, He will not get any domains yet as his domain is not approved".ljust(200) + "****Test Passed  <<9>>***" + "\n"
		cprint(_str, "green")
else:
		_str = "Get request by user_two failed, as he didnt receive emppty list of domains".ljust(200) + "****Test Failed***" + "\n"
		cprint(_str, "red")



logger.info("Test")
r = requests.put("%s/%s"%(DOMAIN_URL, domains_object["user_two"]["module_id"]), data=json.dumps({"user_id": users["user_two"]["user_id"], "creation_approval": True}))
cprint ("domain Admin<<%s>> and domain user_two <<%s>> are not creation_approval by user_two"%(domains_object["admin"]["module_id"], domains_object["user_two"]["module_id"]), "green")
cprint ("Marking domain user_two <<%s>> creation_approval by superadmin"%(domains_object["user_two"]["module_id"]), "green")
if r.json()["error"]:
		_str = "Creation approval request by user_two failed, he wasnt able to maark creation_approval".ljust(200) + "****Test Passed <<10>>***" + "\n"
		cprint(_str, "green")
else:
		_str = "Get request by user_two failed, as he didnt receive emppty list of domains".ljust(200) + "****Test Failed***" + "\n"
		cprint(_str, "red")



logger.info("Test")
r = requests.put("%s/%s"%(DOMAIN_URL, domains_object["user_two"]["module_id"]), data=json.dumps({"user_id": users["superadmin"]["user_id"], "creation_approval": True}))
cprint ("domain Admin<<%s>> and domain user_two <<%s>> are not creation_approval by superadmin"%(domains_object["admin"]["module_id"], domains_object["user_two"]["module_id"]), "green")
cprint ("Marking domain user_two <<%s>> creation_approval by superadmin"%(domains_object["user_two"]["module_id"]), "green")
if not r.json()["error"]:
		_str = "Creation approval by superadmin succeeded".ljust(200) + "****Test Passed <<11>>***" + "\n"
		cprint(_str, "green")
else:
		_str = "Creation approval by superadmin failed".ljust(200) + "****Test Failed***" + "\n"
		cprint(_str, "red")




logger.info("Test")
r = requests.get(DOMAIN_URL, params={"user_id": users["user_two"]["user_id"]})
cprint ("Now the domain created by user_two has been creation_approval by superadmin", "green")
cprint ("He must get a domain whose domain id must match with on ehe created", "green")
if r.json()["data"]["module_ids"][0] == domains_object["user_two"]["module_id"]:
		_str = "Get request by user_two, He will get a domain which he created as it is approved sy superadmin".ljust(200) + "****Test Passed <<12>>***" + "\n"
		cprint(_str, "green")
else:
		_str = "Get request by user_two failed, as he didnt receive emppty list of domains".ljust(200) + "****Test Failed***" + "\n"
		cprint(_str, "red")




logger.info("Test")
r = requests.get(DOMAIN_URL, params={"user_id": users["user_two"]["user_id"]})
cprint ("Now the domain created by user_two has been creation_approval by superadmin", "green")
cprint ("He must get a domain whose domain id must match with on ehe created", "green")
if r.json()["data"]["module_ids"][0] == domains_object["user_two"]["module_id"]:
		_str = "Get request by user_two, He will get a domain which he created as it is approved sy superadmin".ljust(200) + "****Test Passed <<13>>***" + "\n"
		cprint(_str, "green")
else:
		_str = "Get request by user_two failed, as he didnt receive emppty list of domains".ljust(200) + "****Test Failed***" + "\n"
		cprint(_str, "red")







logger.info("Test")
r = requests.get("%s/%s"%(DOMAIN_PERMISSIONSURL, domains_object["user_two"]["module_id"]))
cprint ("Now the domain created by user_two has been creation_approval by superadmin", "green")
cprint ("He must get a domain whose domain id must match with on ehe created", "green")
if len(r.json()["data"]) == 3 :
		_str = "Permisisons for doman created by user_two has three domanins list with permission of admin, supeamdin and user_two".ljust(200) + "****Test Passed <<14>>***" + "\n"
		cprint(_str, "green")
else:
		_str = "Get request by user_two failed, as he didnt receive emppty list of domains".ljust(200) + "****Test Failed***" + "\n"
		cprint(_str, "red")
logger.info("Test")


r = requests.get(DOMAIN_PERMISSIONSURL, params={"user_id": users["admin"]["user_id"]})
cprint ("get permissions for the admin for module_type domain", "green")
cprint ("As till now, nobody provided admin any permissions, he will have get permission on every domain", "green")
if len(r.json()["data"]) == 3 and r.json()["data"][0]["permission"] == {"get": True, "add_child": False, "delete": False, "edit": False}:
		_str = "NUmber of domains with permission object which admin got is three".ljust(200) + "****Test Passed  <<15>>***" + "\n"
		cprint(_str, "green")
else:
		_str = "Get request by user_two failed, as he didnt receive emppty list of domains".ljust(200) + "****Test Failed***" + "\n"
		cprint(_str, "red")




r = requests.get(DOMAIN_URL, params={"user_id": users["admin"]["user_id"]})
cprint ("admin will try to provide permission to user_one on domain created by user_two", "green")
cprint ("The request will fail as admin doesnt have the permission delete permission on domain created by user two", "green")
cprint ("This is the domains admin got on which he have get and delete permissions, he got only two as one of the domain is still not creation approval by superadmin", "green")
if len(r.json()["data"]) == 2 and r.json()["data"]["modules"][0]["permission"] == {"get": True, "add_child": False, "delete": False, "edit": False}:
		_str = "NUmber of domains with permission object which admin got is TWO".ljust(200) + "****Test Passed <<16>>***" + "\n"
		cprint(_str, "green")
else:
		_str = "Get request by user_two failed, as he didnt receive emppty list of domains".ljust(200) + "****Test Failed***" + "\n"
		cprint(_str, "red")


permission = {"get": True, "delete": True, "add_child": False, "edit": False}
pprint ("%s/%s"%(DOMAIN_URL,domains_object["user_two"]["module_id"]))
r = requests.put("%s/%s"%(DOMAIN_URL, domains_object["user_two"]["module_id"] ), data=json.dumps({"user_id": users["admin"]["user_id"], "granter_id": users["superadmin"]["user_id"],"permission": permission}))
cprint ("Now the superadmin will give permission to admin for the deletion on domain created by user_two", "green")
cprint ("After this result admin %s will have delete permission on %s"%(users["admin"]["user_id"], domains_object["user_two"]["module_id"]), "green")



r = requests.get(DOMAIN_URL, params={"user_id": users["admin"]["user_id"]})
cprint ("Checking if domain permissions of admin has been changed on domain %s"%domains_object["user_two"]["module_id"], "green")
pprint (r.json()["data"]["modules"][1]["permission"])
if len(r.json()["data"]) == 2 and r.json()["data"]["modules"][1]["permission"] == {"permission": {"get": True, "add_child": False, "delete": True, "edit": False}}:
		_str = "The admin now has delete permission on the domain %s"%domains_object["user_two"]["module_id"].ljust(100) + "****Test Passed <<17>>***" + "\n"
		cprint(_str, "green")
else:
		_str = "Get request by user_two failed, as he didnt receive emppty list of domains".ljust(200) + "****Test Failed***" + "\n"
		cprint(_str, "red")




r = requests.get(DOMAIN_URL, params={"user_id": users["user_one"]["user_id"]})
cprint ("Checking get modules for user_one %s"%(users["user_one"]["user_id"]), "green")
if len(r.json()["data"]["module_ids"]) == 0:
		message = "The user_one %s havent received any domain, as he desnt have any permission on any domain, neither he created any"%users["user_one"]["user_id"]
		_str = message.ljust(200) + "****Test Passed <<18>>***" + "\n"
		cprint(_str, "green")
else:
		_str = "Get request by user_two failed, as he didnt receive emppty list of domains".ljust(200) + "****Test Failed***" + "\n"
		cprint(_str, "red")



permission = {"get": True, "delete": False, "add_child": True, "edit": False}
pprint ("%s/%s"%(DOMAIN_URL,domains_object["user_two"]["module_id"]))
r = requests.put("%s/%s"%(DOMAIN_URL, domains_object["user_two"]["module_id"] ), data=json.dumps({"user_id": users["user_one"]["user_id"], "granter_id": users["admin"]["user_id"],"permission": permission}))
cprint ("Now the admin will give permission to user_one for the add_child, get on domain created by user_two", "green")
cprint ("After this result admin %s will have delete permission on %s"%(users["admin"]["user_id"], domains_object["user_two"]["module_id"]), "green")
if r.json()["error"]:
		message = "The admin doesnt haven add_child permisisons on domain %s so he cant provide ad child permission to user_one %s"%(domains_object["user_two"]["module_id"],users["user_one"]["user_id"])
		_str = message.ljust(200) + "****Test Passed <<19>>***" + "\n"
		cprint(_str, "green")
else:
		print (r.json())
		_str = "".ljust(200) + "****Test Failed***" + "\n"
		cprint(_str, "red")















permission = {"get": True, "delete": False, "add_child": False, "edit": False}
pprint ("%s/%s"%(DOMAIN_URL,domains_object["user_two"]["module_id"]))
r = requests.put("%s/%s"%(DOMAIN_URL, domains_object["user_two"]["module_id"] ), data=json.dumps({"user_id": users["user_one"]["user_id"], "granter_id": users["admin"]["user_id"],"permission": permission}))
cprint ("Now the admin will give <<GET>>permission to user_one %s on domain created by user_two %s"%(users["user_one"]["user_id"], domains_object["user_two"]["module_id"]), "green")
cprint ("After this result user_one %s will have get permission on %s"%(users["user_one"]["user_id"], domains_object["user_two"]["module_id"]), "green")

if r.json()["success"]:
		message = "The admin had get permisisons on domain %s so he provided get permission to user_one %s"%(domains_object["user_two"]["module_id"],users["user_one"]["user_id"])
		_str = message.ljust(200) + "****Test Passed <<20>>***" + "\n"
		cprint(_str, "green")
else:
		_str = "Get request by user_two failed, as he didnt receive emppty list of domains".ljust(200) + "****Test Failed***" + "\n"
		cprint(_str, "red")


r = requests.get(DOMAIN_URL, params={"user_id": users["user_one"]["user_id"]})
cprint ("Checking get modules for user_one, NOw will get a domain created by user_two as admin provied get permisison to user_one", "green")
if len(r.json()["data"]["module_ids"]) == 1:
		message = "The user_one %s received a domain %s"%(users["user_one"]["user_id"], domains_object["user_two"]["module_id"])
		_str = message.ljust(200) + "****Test Passed <<21>>***" + "\n"
		cprint(_str, "green")
		
else:
		cprint(_str, "green")
		_str = "Get request by user_two failed, as he didnt receive emppty list of domains".ljust(200) + "****Test Failed***" + "\n"
		cprint(_str, "red")





##Providing add child permission to user_one by superadmin, A thing to note is 
##the permissions will be updated through set_obj, so all the previoud permissions
## will be overidden by superadmin permissions pobject given to this user
permission = {"get": True, "delete": False, "add_child": True, "edit": True}
pprint ("%s/%s"%(DOMAIN_URL,domains_object["user_two"]["module_id"]))
r = requests.put("%s/%s"%(DOMAIN_URL, domains_object["user_two"]["module_id"] ), data=json.dumps({"user_id": users["user_one"]["user_id"], "granter_id": users["superadmin"]["user_id"],"permission": permission}))
cprint ("Now the admin will give <<GET>>permission to user_one %s on domain created by user_two %s"%(users["user_one"]["user_id"], domains_object["user_two"]["module_id"]), "green")
cprint ("After this result user_one %s will have get permission on %s"%(users["user_one"]["user_id"], domains_object["user_two"]["module_id"]), "green")

if r.json()["success"]:
		message = "The admin had get permisisons on domain %s so he provided get permission to user_one %s"%(domains_object["user_two"]["module_id"],users["user_one"]["user_id"])
		_str = message.ljust(200) + "****Test Passed <<20>>***" + "\n"
		cprint(_str, "green")
else:
		_str = "Get request by user_two failed, as he didnt receive emppty list of domains".ljust(200) + "****Test Failed***" + "\n"
		cprint(_str, "red")







##Providing add child permission to user_one by superadmin, A thing to note is 
##the permissions will be updated through set_obj, so all the previoud permissions
## will be overidden by superadmin permissions pobject given to this user
r = requests.get(DOMAIN_URL, params={"user_id": users["user_one"]["user_id"]})
cprint ("Checking get modules for user_one, NOw will get a domain created by user_two as admin provied get permisison to user_one", "green")
if len(r.json()["data"]["module_ids"]) == 1:
		message = "The user_one %s received a domain %s"%(users["user_one"]["user_id"], domains_object["user_two"]["module_id"])
		_str = message.ljust(200) + "****Test Passed <<21>>***" + "\n"
		cprint(_str, "green")
		
else:
		cprint(_str, "green")
		_str = "Get request by user_two failed, as he didnt receive emppty list of domains".ljust(200) + "****Test Failed***" + "\n"
		cprint(_str, "red")



import progressbar
import time

bar = progressbar.ProgressBar(redirect_stdout=True)


concepts = []
pprint ("Adding concepts")
for i in range(1):
	domain = random.choice([("user_two", domains_object["user_two"]["module_id"]),   ("admin", domains_object["admin"]["module_id"]), ("superadmin", domains_object["superadmin"]["module_id"])])
	r = requests.post("http://localhost:8000/concepts", data=json.dumps({"module_name": "%s"%fake.name(), 
														"parent_id": domain[1],
														 "description": fake.text(), 
														 "user_id": users["superadmin"]["user_id"]}))
	bar.update(i*100/50)
	if r.status_code == 200:
		concepts.append((domain[0], domain[1], r.json()["data"] ))

	


bar = progressbar.ProgressBar(redirect_stdout=True)
pprint ("Adding subconcepts")
subconcepts = []
for i in range(1):
	concept = random.choice(concepts)
	r = requests.post("http://localhost:8000/subconcepts", data=json.dumps({"module_name": "%s"%fake.name(), 
														"parent_id": concept[2]["module_id"],
														 "description": fake.text(), 
														 "user_id": users["superadmin"]["user_id"]}))
	bar.update(i*100/10)
	subconcepts.append((concept[0], concept[1], concept[2], r.json()["data"] ))


bar = progressbar.ProgressBar(redirect_stdout=True)
pprint ("Adding nanoskills")
nanoskills = []
for i in range(1):
	#subconcept = random.choice(subconcepts)
	subconcept = subconcepts[0]
	r = requests.post("http://localhost:8000/nanoskills", data=json.dumps({"module_name": "%s"%fake.name(), 
														"parent_id": subconcept[3]["module_id"],
														 "description": fake.text(), 
														 "user_id": users["superadmin"]["user_id"]}))
	bar.update(i*100/10)
	nanoskills.append((subconcept[0], subconcept[1], subconcept[2], subconcept[3], r.json()["data"] ))

for i in nanoskills:
	print (i[4]["module_id"])




bar = progressbar.ProgressBar(redirect_stdout=True)
pprint ("Adding Questions")
questions = []
for i in range(100):
	nanoskill = random.choice(nanoskills)
	r = requests.post("http://localhost:8000/questions", data=json.dumps({"module_name": "%s"%fake.name(), 
														"question_type": "multiple_choice",
														"question_text": fake.text(),
														"options": [fake.paragraph(), fake.paragraph(), fake.paragraph(), fake.paragraph()],
														"parent_id": nanoskill[4]["module_id"],
														 "description": fake.text(), 
														 "user_id": users["superadmin"]["user_id"]}))

	bar.update(i*100/100)
	questions.append((nanoskill[0], nanoskill[1], nanoskill[2], nanoskill[3], nanoskill[4], r.json()["data"] ))



#pprint (subconcepts[3][3]["parent_id"])
#pprint (subconcepts[3][3]["module_id"])
pprint (users["superadmin"]["user_id"])
#r = requests.delete("http://localhost:8000/subconcepts", params={"module_id": subconcepts[3][3]["module_id"], "user_id": users["superadmin"]["user_id"]})
r = requests.delete("http://localhost:8000/questions", params={"module_id": questions[0][5]["module_id"], "user_id": users["superadmin"]["user_id"]})
pprint (r.json())


"""

bar = progressbar.ProgressBar(redirect_stdout=True)
pprint ("Adding questions")
nanoskills = []
for i in range(1000):
	subconcept = random.choice(subconcepts)
	r = requests.post("http://localhost:8000/nanoskills", data=json.dumps({"module_name": "%s"%fake.name(), 
														"parent_id": subconcept[3]["module_id"],
														 "description": fake.text(), 
														 "user_id": users["superadmin"]["user_id"]}))
	bar.update(i*100/1000)
	nanoskills.append((subconcept[0], subconcept[1], subconcept[2], subconcept[3], r.json()["data"] ))






r = requests.get(DOMAIN_URL, params={"user_id": users["admin"]["user_id"]})
r = requests.get(DOMAIN_URL, params={"user_id": users["admin"]["user_id"]})
cprint ("Now Admin will give permission to user_one for the deletion on domain created by user_two", "green")
cprint ("After this result user_one %s will have delete permission on %s"%(users["user_one"]["user_id"], domains_object["user_two"]["module_id"]), "green")



r = requests.get(DOMAIN_URL, params={"user_id": users["superadmin"]["user_id"]})
cprint ("Now superadmin will delete the admin", "green")
cprint ("After this result user_one %s will have delete permission on %s"%(users["user_one"]["user_id"], domains_object["user_two"]["module_id"]), "green")



r = requests.get(CONCEPT_URL, params={"user_id": users["superadmin"]["user_id"]})
cprint ("user_one will try to create a concpet on domain created by user_two", "green")
cprint ("He will fail as he doesnt have add_child permission on this domain", "green")



r = requests.get(CONCEPT_URL, params={"user_id": users["superadmin"]["user_id"]})
cprint ("user_two will try to create a concpet on domain created by him", "green")
cprint ("He will succeed as he himself created this domain and creator gets all the permissions excpet the delete permission", "green")



r = requests.get(CONCEPT_URL, params={"user_id": users["superadmin"]["user_id"]})
cprint ("user_one will try to edit a concpet  created by user_two, hw will not see it too", "green")
cprint ("He will fail as he doesnt have edit permissions on this subconcept", "green")



r = requests.get(CONCEPT_URL, params={"user_id": users["superadmin"]["user_id"]})
cprint ("user_two will pass on edit, add_child, permissions to user_one on the concept created by him", "green")
cprint ("He will fail as he doesnt have edit permissions on this subconcept", "green")


r = requests.get(CONCEPT_URL, params={"user_id": users["superadmin"]["user_id"]})
cprint ("user_one will now try to edit the concept name and try to set it to concept name present in the database", "green")
cprint ("He will fail as creating a module with same name in same module_type is not allowed", "green")





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
r = requests.get("http://localhost:8000/domains", params={"user_id": users["admin"]["user_id"]})
cprint(r.json()["data"]["module_ids"], "green")


logger.error("Now checking if user_two is getting his domain, he will get it even if its pending approval")
r = requests.get("http://localhost:8000/domains", params={"user_id": users["user_two"]["user_id"]})
pprint(r.json())

logger.error("User one will not see any domain as he doesnt have any permission on any domain neither he created one")
r = requests.get("http://localhost:8000/domains", params={"user_id": users["user_one"]["user_id"]})
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



concepts = {}
r = requests.post("http://localhost:8000/concepts", data=json.dumps({"module_name": "concept-%s"%fake.name(), "parent_id": domains["user_two_domain"]["module_id"],\
														 "description": fake.text(), "user_id": users["superadmin"]["user_id"]}))

pprint (r.json()["data"])
concepts.update({"concept_by_superadmin_one":r.json()["data"] })

r2 = requests.post("http://localhost:8000/concepts", data=json.dumps({"module_name": "concept-%s"%fake.name(), "parent_id": domains["user_two_domain"]["module_id"],\
														 "description": fake.text(), "user_id": users["superadmin"]["user_id"]}))
pprint (r.json()["data"])
concepts.update({"concept_by_superadmin_two":r.json()["data"] })




##Trying to crate concept from admin user id
r2 = requests.post("http://localhost:8000/concepts", data=json.dumps({"module_name": "concept-%s"%fake.name(), "parent_id": domains["admin_domain"]["module_id"],\
														 "description": fake.text(), "user_id": users["admin"]["user_id"]}))
pprint (r.json()["data"])
concepts.update({"concept_by_admin_one":r.json()["data"] })



r2 = requests.post("http://localhost:8000/concepts", data=json.dumps({"module_name": "concept-%s"%fake.name(), "parent_id": domains["user_two_domain"]["module_id"],\
														 "description": fake.text(), "user_id": users["superadmin"]["user_id"]}))
pprint (r.json()["data"])
concepts.update({"concept_by_superadmin_three":r.json()["data"] })



##trying to create concepts by other users 
r = requests.post("http://localhost:8000/concepts", data=json.dumps({"module_name": "concept-%s"%fake.name(), "parent_id": domains["user_two_domain"]["module_id"],\
														 "description": fake.text(), "user_id": users["user_one"]["user_id"]}))
pprint (r.json()["data"])

r = requests.post("http://localhost:8000/concepts", data=json.dumps({"module_name": "concept-%s"%fake.name(), "parent_id": domains["user_two_domain"]["module_id"],\
														 "description": fake.text(), "user_id": users["user_two"]["user_id"]}))
pprint (r.json()["data"])

r = requests.post("http://localhost:8000/concepts", data=json.dumps({"module_name": "concept-%s"%fake.name(), "parent_id": domains["user_two_domain"]["module_id"],\
														 "description": fake.text(), "user_id": users["admin"]["user_id"]}))


##adding subconcepts randomly on concept ids by superadmin and admin
########################## Subconcepts #################################

########################## subceoncept by superadmin on concept_by_superadmin_three ##################################################3
subconcepts = {}
r = requests.post("http://localhost:8000/subconcepts", data=json.dumps({"module_name": "subconcept-%s"%fake.name(), "parent_id": concepts["concept_by_superadmin_three"]["module_id"],\
														 "description": fake.text(), "user_id": users["superadmin"]["user_id"]}))

pprint (r.json()["data"])
subconcepts.update({"subconcept_by_superadmin_one":r.json()["data"] })

########################## subceoncept by superadmin on concept_by_superadmin_two and its key is subconcept_by_superadmin_two ##################################################3

r = requests.post("http://localhost:8000/subconcepts", data=json.dumps({"module_name": "subconcept-%s"%fake.name(), "parent_id": concepts["concept_by_superadmin_two"]["module_id"],\
														 "description": fake.text(), "user_id": users["superadmin"]["user_id"]}))

pprint (r.json()["data"])
subconcepts.update({"subconcept_by_superadmin_two":r.json()["data"] })

########################## subconcept by superadmin on concept_by_superadmin_three and its key is subconcept_by_superadmin_three ##################################################3
r = requests.post("http://localhost:8000/subconcepts", data=json.dumps({"module_name": "subconcept-%s"%fake.name(), "parent_id": concepts["concept_by_superadmin_three"]["module_id"],\
														 "description": fake.text(), "user_id": users["superadmin"]["user_id"]}))

pprint (r.json()["data"])
subconcepts.update({"subconcept_by_superadmin_three":r.json()["data"] })

########################## subconcept by superadmin on concept_by_superadmin_one and its key is subconcept_by_superadmin_four ##################################################3
r = requests.post("http://localhost:8000/subconcepts", data=json.dumps({"module_name": "subconcept-%s"%fake.name(), "parent_id": concepts["concept_by_superadmin_one"]["module_id"],\
														 "description": fake.text(), "user_id": users["superadmin"]["user_id"]}))

pprint (r.json()["data"])
subconcepts.update({"subconcept_by_superadmin_four":r.json()["data"] })


########################## subconcept by superadmin on concept_by_superadmin_one and its key is subconcept_by_superadmin_five ##################################################3
r = requests.post("http://localhost:8000/subconcepts", data=json.dumps({"module_name": "subconcept-%s"%fake.name(), "parent_id": concepts["concept_by_superadmin_one"]["module_id"],\
														 "description": fake.text(), "user_id": users["superadmin"]["user_id"]}))

pprint (r.json()["data"])
subconcepts.update({"subconcept_by_superadmin_five":r.json()["data"] })



########################## subconcept by superadmin on concept_by_superadmin_three and its key is subconcept_by_superadmin_six ##################################################3
r = requests.post("http://localhost:8000/subconcepts", data=json.dumps({"module_name": "subconcept-%s"%fake.name(), "parent_id": concepts["concept_by_superadmin_three"]["module_id"],\
														 "description": fake.text(), "user_id": users["superadmin"]["user_id"]}))

pprint (r.json()["data"])
subconcepts.update({"subconcept_by_superadmin_six":r.json()["data"] })



##########################################******************* Nanoskills *****************#################################################
#['subconcept_by_superadmin_three', 'subconcept_by_superadmin_one', 'subconcept_by_superadmin_four', 'subconcept_by_superadmin_two',\
# 'subconcept_by_superadmin_five', 'subconcept_by_superadmin_six']

nanoskills = {}
########################## subconcept by superadmin on concept_by_superadmin_three and its key is subconcept_by_superadmin_six ##################################################3
r = requests.post("http://localhost:8000/nanoskills", data=json.dumps({"module_name": "nanoskill-%s"%fake.name(), "parent_id": subconcepts["subconcept_by_superadmin_three"]["module_id"],\
														 "description": fake.text(), "user_id": users["superadmin"]["user_id"]}))

pprint (r.json()["data"])
nanoskills.update({"nanoskill_by_superadmin_one":r.json()["data"] })



########################## subconcept by superadmin on concept_by_superadmin_three and its key is subconcept_by_superadmin_six ##################################################3
r = requests.post("http://localhost:8000/nanoskills", data=json.dumps({"module_name": "nanoskill-%s"%fake.name(), "parent_id": subconcepts["subconcept_by_superadmin_one"]["module_id"],\
														 "description": fake.text(), "user_id": users["superadmin"]["user_id"]}))

pprint (r.json()["data"])
nanoskills.update({"nanoskill_by_superadmin_two":r.json()["data"] })



########################## subconcept by superadmin on concept_by_superadmin_three and its key is subconcept_by_superadmin_six ##################################################3
r = requests.post("http://localhost:8000/nanoskills", data=json.dumps({"module_name": "nanoskill-%s"%fake.name(), "parent_id": subconcepts["subconcept_by_superadmin_two"]["module_id"],\
														 "description": fake.text(), "user_id": users["superadmin"]["user_id"]}))

pprint (r.json()["data"])
nanoskills.update({"nanoskill_by_superadmin_three":r.json()["data"] })


########################## subconcept by superadmin on concept_by_superadmin_three and its key is subconcept_by_superadmin_six ##################################################3
r = requests.post("http://localhost:8000/nanoskills", data=json.dumps({"module_name": "nanoskill-%s"%fake.name(), "parent_id": subconcepts["subconcept_by_superadmin_two"]["module_id"],\
														 "description": fake.text(), "user_id": users["superadmin"]["user_id"]}))

pprint (r.json()["data"])
nanoskills.update({"nanoskill_by_superadmin_four":r.json()["data"] })


########################## subconcept by superadmin on concept_by_superadmin_three and its key is subconcept_by_superadmin_six ##################################################3
r = requests.post("http://localhost:8000/nanoskills", data=json.dumps({"module_name": "nanoskill-%s"%fake.name(), "parent_id": subconcepts["subconcept_by_superadmin_two"]["module_id"],\
														 "description": fake.text(), "user_id": users["superadmin"]["user_id"]}))

pprint (r.json()["data"])
nanoskills.update({"nanoskill_by_superadmin_five":r.json()["data"] })



########################## subconcept by superadmin on concept_by_superadmin_three and its key is subconcept_by_superadmin_six ##################################################3
r = requests.post("http://localhost:8000/nanoskills", data=json.dumps({"module_name": "nanoskill-%s"%fake.name(), "parent_id": subconcepts["subconcept_by_superadmin_two"]["module_id"],\
														 "description": fake.text(), "user_id": users["superadmin"]["user_id"]}))

pprint (r.json()["data"])
nanoskills.update({"nanoskill_by_superadmin_six":r.json()["data"] })



########################## subconcept by superadmin on concept_by_superadmin_three and its key is subconcept_by_superadmin_six ##################################################3
r = requests.post("http://localhost:8000/nanoskills", data=json.dumps({"module_name": "nanoskill-%s"%fake.name(), "parent_id": subconcepts["subconcept_by_superadmin_two"]["module_id"],\
														 "description": fake.text(), "user_id": users["superadmin"]["user_id"]}))

pprint (r.json()["data"])
nanoskills.update({"nanoskill_by_superadmin_seven":r.json()["data"] })



########################## subconcept by superadmin on concept_by_superadmin_three and its key is subconcept_by_superadmin_six ##################################################3
r = requests.post("http://localhost:8000/nanoskills", data=json.dumps({"module_name": "nanoskill-%s"%fake.name(), "parent_id": subconcepts["subconcept_by_superadmin_four"]["module_id"],\
														 "description": fake.text(), "user_id": users["superadmin"]["user_id"]}))

pprint (r.json()["data"])
nanoskills.update({"nanoskill_by_superadmin_eight":r.json()["data"] })



########################## subconcept by superadmin on concept_by_superadmin_three and its key is subconcept_by_superadmin_six ##################################################3
r = requests.post("http://localhost:8000/nanoskills", data=json.dumps({"module_name": "nanoskill-%s"%fake.name(), "parent_id": subconcepts["subconcept_by_superadmin_five"]["module_id"],\
														 "description": fake.text(), "user_id": users["superadmin"]["user_id"]}))

pprint (r.json()["data"])
nanoskills.update({"nanoskill_by_superadmin_nine":r.json()["data"] })


########################## subconcept by superadmin on concept_by_superadmin_three and its key is subconcept_by_superadmin_six ##################################################3
r = requests.post("http://localhost:8000/nanoskills", data=json.dumps({"module_name": "nanoskill-%s"%fake.name(), "parent_id": subconcepts["subconcept_by_superadmin_one"]["module_id"],\
														 "description": fake.text(), "user_id": users["superadmin"]["user_id"]}))

pprint (r.json()["data"])
nanoskills.update({"nanoskill_by_superadmin_ten":r.json()["data"] })


########################## subconcept by superadmin on concept_by_superadmin_three and its key is subconcept_by_superadmin_six ##################################################3
r = requests.post("http://localhost:8000/nanoskills", data=json.dumps({"module_name": "nanoskill-%s"%fake.name(), "parent_id": subconcepts["subconcept_by_superadmin_two"]["module_id"],\
														 "description": fake.text(), "user_id": users["superadmin"]["user_id"]}))

pprint (r.json()["data"])
nanoskills.update({"nanoskill_by_superadmin_eleven":r.json()["data"] })


########################## subconcept by superadmin on concept_by_superadmin_three and its key is subconcept_by_superadmin_six ##################################################3
r = requests.post("http://localhost:8000/nanoskills", data=json.dumps({"module_name": "nanoskill-%s"%fake.name(), "parent_id": subconcepts["subconcept_by_superadmin_three"]["module_id"],\
														 "description": fake.text(), "user_id": users["superadmin"]["user_id"]}))

pprint (r.json()["data"])
nanoskills.update({"nanoskill_by_superadmin_twelve":r.json()["data"] })



pprint (r.json()["data"])
pprint (users)
pprint(domains)
pprint (concepts)
print (subconcepts.keys())
"""
if __name__ == "__main__":
	pass



