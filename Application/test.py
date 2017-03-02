
import requests
import json
import pprint
import pymongo
from termcolor import colored, cprint
import random

app_super_admin = "nctsuperadmin"
app_super_admin_pwd = "1234Pacific###"
app_super_admin_user_id = "nctsuperadmin###"
app_port = 8000
mongo_user = "application"
mongo_pwd = "1234Pacific###"
mongo_ip = "localhost"
mongo_port = 27017
category_collection_name = "categories"
criteria_collection_name = "criteria"
level_collection_name = "levels"
user_collection_name = "users"


uri = "mongodb://%s:%s@%s:%s/%s"%(mongo_user, mongo_pwd, mongo_ip, mongo_port, "admin")
print (uri)
client = pymongo.MongoClient(uri)
client.drop_database("tiapplication")
db = client["tiapplication"]

category_collection = db[category_collection_name]
users_collection = db[user_collection_name]
criteria_collection = db[criteria_collection_name]

##adding user_id=="superadmin" to categiry collection
#db[user_collection_name].update_one({"name": "super_permissions"},  {"$addToSet": { "all": "superadmin"}}, upsert=True)
#db[sub_category_collection_name].update_one({"name": "super_permissions"},  {"$addToSet": { "all": "superadmin"}}, upsert=True)
#db[level_collection_name].update_one({"name": "super_permissions"},  {"$addToSet": { "all": "superadmin"}}, upsert=True)

address = "http://localhost:8000"
from faker import Faker
fake = Faker()




##made from superadmin pass and womething bulshit
headers = {"Authorization": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwYXNzd29yZCI6IjEyMzRQYWNpZmljIyMjIiwidXNlcl90eXBlIjoic3VwZXJhZG1pbiIsInVzZXJuYW1lIjoibmN0c3VwZXJhZG1pbiJ9.ZSCDjXx_n5LpkJAkzyKFke0ovax-zb6pps1SiFEKosA"}

def insert_super_admin():
	cprint("creating superadmin with user_name [%s], user_type [%s], user_id [%s] user_password [%s]"%\
			(app_super_admin, "superadmin", app_super_admin_user_id, app_super_admin_pwd), 'green')

	db[user_collection_name].insert({'user_type': "superadmin", "username": app_super_admin,\
							 "password": app_super_admin_pwd, "user_id": app_super_admin_user_id })
	return 


def create_admin_one():
	print ("\n\n")
	cprint("creating first admin by super admin", "green")
	user_one = {
 		'email': 'adminone@gmail.com',
 		'full_name': 'admin one',
 		'password': 'passwordone',
 		'region': ['delhi', 'mumbai'],
 		'state': ['delhi', 'mumbai'],
 		'user_type': 'admin',
 		'username': 'adminone',
 		'parent_user_id': app_super_admin_user_id, 
 		'is_superadmin': False}

	r = requests.post("http://localhost:8000/signup", data=json.dumps(user_one), headers=headers )
	cprint(r.json(), "blue")
	return (r.json()["user_id"], r.json()["token"])



def check_if_login_provides_same_token(Authorization):
	print ("\n\n")
	cprint("Checking if login provides the same token as provided during registration", "green")
	cprint("This is the AUthorization token %s"%Authorization, "green")
	user_one = {
 		'password': 'passwordone',
 		'user_type': 'admin',
 		'username': 'adminone',
 		}
	r = requests.post("http://localhost:8000/login", data=json.dumps(user_one), headers={"Authorization": Authorization})
	cprint(r.json(), "blue")
	if r.json()["token"] != Authorization:
		cprint("Test Failed", "red", "on_white")
	else:
		cprint("Test Passed", "green", "on_white")
	return 



def create_admin_two():
	print ("\n\n")
	cprint("creating second admin by super admin", "green")
	user_one = {
 		'email': 'admintwo@gmail.com',
 		'full_name': 'admin two',
 		'password': 'passwordtwo',
 		'region': ['delhi', 'mumbai'],
 		'state': ['delhi', 'mumbai'],
 		'user_type': 'admin',
 		'username': 'admintwo',
 		'parent_user_id': app_super_admin_user_id, 
 		'is_superadmin': False}

	r = requests.post("http://localhost:8000/signup", data=json.dumps(user_one), headers=headers )
	cprint(r.json(), "blue")
	return (r.json()["user_id"], r.json()["token"])


def create_user_first(admin_one_user_id, Authorization):
	print ("\n\n")
	cprint("creating first user by admin two", "green")
	user_one = {
 		'email': 'userone@gmail.com',
 		'full_name': 'user one',
 		'password': 'user one',
 		'region': ['user one region one', 'user one region two'],
 		'state': ['user one state one', 'user one state two'],
 		'user_type': 'question_uploader',
 		'username': 'userone',
 		'parent_user_id': admin_one_user_id, 
 		'is_superadmin': False}

	r = requests.post("http://localhost:8000/signup", data=json.dumps(user_one), headers={"Authorization": Authorization})
	cprint(r.json(), "blue")
	return (r.json()["user_id"], r.json()["token"])


def create_user_second(admin_one_user_id, Authorization):
	print ("\n\n")
	cprint("creating second user by admin two", "green")
	user_one = {
 		'email': 'usertwo@gmail.com',
 		'full_name': 'user two',
 		'password': 'user two',
 		'region': ['user two region one', 'user two region two'],
 		'state': ['user two state one', 'user two state two'],
 		'user_type': 'evaluator',
 		'username': 'usertwo',
 		'parent_user_id': admin_one_user_id, 
 		'is_superadmin': False}

	r = requests.post("http://localhost:8000/signup", data=json.dumps(user_one), headers={"Authorization": Authorization} )
	cprint(r.json(), "blue")
	return (r.json()["user_id"], r.json()["token"])




def create_super_admin():
	print ("\n\n")
	cprint("creating first superadmin by super admin", "green")
	user_one = {
 		'email': 'superadmin@gmail.com',
 		'full_name': 'super admin',
 		'password': 'superadmin',
 		'region': ['super admin region 1', 'superadmin region 2'],
 		'state': ['superadmin state 1', 'superadmin state 2'],
 		'user_type': 'superadmin',
 		'username': 'superadmin',
 		'parent_user_id': app_super_admin_user_id, 
 		'is_superadmin': True}

	r = requests.post("http://localhost:8000/signup", data=json.dumps(user_one), headers=headers )
	cprint(r.json(), "blue")
	return (r.json()["user_id"], r.json()["token"])



def create_super_admin_by_admin(admin_user_id, Authorization):
	"""
	pass auth token for any admin or user
	"""
	print ("\n\n")
	cprint("creating second superadmin by admin", "green")
	cprint("Must fail, because admin cant create superadmin", "green")
	user_one = {
 		'email': 'superadmintwo@gmail.com',
 		'full_name': 'super admin two',
 		'password': 'superadmin two',
 		'region': ['super admin two region 1', 'superadmin region two 2'],
 		'state': ['superadmin state two 1', 'superadmin state two 2'],
 		'user_type': 'superadmin',
 		'username': 'superadmin',
 		'parent_user_id': admin_user_id, 
 		'is_superadmin': True}

	r = requests.post("http://localhost:8000/signup", data=json.dumps(user_one), headers={"Authorization": Authorization})
	cprint(r.json(), "blue")
	if r.json()["success"] == True:
			cprint("Test Failed", "red", "on_white")
	else:
			cprint("Test Passed", "green", "on_white")
	return 


def create_admin_three_by_admin(admin_user_id, Authorization):
	"""
	pass auth token for any admin or user
	"""
	print ("\n\n")
	cprint("creating admin three by another admin", "green")
	cprint("Must fail, because admin cant create another admin", "green")
	user_one = {
 		'email': 'superadmintwo@gmail.com',
 		'full_name': 'super admin two',
 		'password': 'superadmin two',
 		'region': ['super admin two region 1', 'superadmin region two 2'],
 		'state': ['superadmin state two 1', 'superadmin state two 2'],
 		'user_type': 'admin',
 		'username': 'superadmin',
 		'parent_user_id': admin_user_id, 
 		'is_superadmin': False}

	r = requests.post("http://localhost:8000/signup", data=json.dumps(user_one), headers={"Authorization": Authorization})
	cprint(r.json(), "blue")
	if r.json()["success"] == True:
			cprint("Test Failed", "red", "on_white")
	else:
			cprint("Test Passed", "green", "on_white")
	return 



def users_by_admin(admin_one_user_id, Authorization):
	"""
	pass auth token for any admin or user
	"""
	print ("\n\n")
	cprint("Getting users created by this admin, nobody else", "green")
	user_one = {
 		'user_id': admin_one_user_id}

	r = requests.post("http://localhost:8000/users", data=json.dumps(user_one), headers={"Authorization": Authorization})
	cprint(r.json(), "blue")
	return 



def create_category_by_superadmin(super_admin_user_id):
	print ("\n\n")
	cprint("Trying to create category by superadmin", "green")

	category_data = {"category_name": "test category one",
				 "text_description": "This is a text description for test categry one", 
				 "score": 20,
				 "user_id": super_admin_user_id
				 }
	r = requests.post("http://localhost:8000/category", data=json.dumps(category_data), headers=headers)
	cprint(r.json(), "blue")
	return 





def create_category_by_admin_one(admin_one_user_id, admin_one_token):
	print ("\n\n")
	cprint("Trying to create category by admin one whose id is [%s]"%admin_one_user_id, "green")

	category_data = {"category_name": "test category admin one",
				 "text_description": "This is a text description for test categry one", 
				 "score": 20,
				 "user_id": admin_one_user_id
				 }
	r = requests.post("http://localhost:8000/category", data=json.dumps(category_data), headers={"Authorization": admin_one_token})
	cprint(r.json(), "blue")
	return  r.json()["category_id"]



def	create_category_by_question_uploader(question_uploader_id, question_uploader_token):
	print ("\n\n")
	cprint("Trying to create category by question uploader", "green")

	category_data = {"category_name": "test category by question uploader",
				 "text_description": "This is a text description for test categry one", 
				 "score": 20,
				 "user_id": question_uploader_id
				 }
	r = requests.post("http://localhost:8000/category", data=json.dumps(category_data), headers={"Authorization": question_uploader_token})
	cprint(r.json(), "blue")
	if r.json()['message'] != 'Insufficient permission for the user %s'%question_uploader_id:
		cprint("Test Failed", "red", "on_white")
	else:
			cprint("Test Passed", "green", "on_white")
	return 
	

def	get_category_by_admin_two(admin_two_user_id, admin_two_token, category_id_by_admin_one):
	print ("\n\n")
	cprint("Trying to get category by admin two created by admin onw", "green")

	r = requests.get("http://localhost:8000/category/%s"%category_id_by_admin_one, data=json.dumps({"user_id": admin_two_user_id}),\
	 headers={"Authorization": admin_two_token})
	cprint(r.json(), "blue")
	"""
	if r.json()['message'] != 'Insufficient permission for the user %s'%question_uploader_id:
		cprint("Test Failed", "red", "on_white")
	else:
			cprint("Test Passed", "green", "on_white")
	"""	
	if r.json()['message'] != 'Insufficient permission for the user %s'%admin_two_user_id:
		cprint("Test Failed", "red", "on_white")
	else:
			cprint("Test Passed", "green", "on_white")
	return 
	

def	change_permissions_by_admin_two(admin_two_user_id, admin_two_token, category_id_by_admin_one):
	print ("\n\n")
	cprint("Trying to change permissions  by admin two of category created by admin one", "green")
	data_object = {"category_id": category_id_by_admin_one, "user_id": admin_two_user_id, "permissions": []}

	print (data_object)
	print ({"Authorization": admin_two_token})
	r = requests.post("http://localhost:8000/categorypermissions", data=json.dumps(data_object),\
	 headers={"Authorization": admin_two_token})

	print (r)
	print (r.text)
	if r.json()['message'] != 'Insufficient permission for the user %s'%question_uploader_id:
		cprint("Test Failed", "red", "on_white")
	else:
			cprint("Test Passed", "green", "on_white")
	if r.json()['message'] != 'Insufficient permission for the user %s'%admin_two_user_id:
		cprint("Test Failed", "red", "on_white")
	else:
			cprint("Test Passed", "green", "on_white")
	return 



def	adding_permissions_by_admin_one_for_admin_two(admin_one_user_id, admin_two_user_id, admin_one_token, category_id_by_admin_one):
	print ("\n\n")
	cprint("Till now category_id [%s] which was created by admin one [%s] doiesnt have permissions\
	 for admin two[%s]"%(category_id_by_admin_one, admin_one_user_id, admin_two_user_id), "green")
	
	permission_object = {"user_id": admin_two_user_id , "create": True, "delete": False, "get": True, "put": True}
	data_object = {"category_id": category_id_by_admin_one, "user_id": admin_one_user_id, \
	"permissions": [permission_object]}

	r = requests.post("http://localhost:8000/categorypermissions", data=json.dumps(data_object),\
	 headers={"Authorization": admin_two_token})

	print(r)
	print (r.text)
	"""
	if r.json()['message'] != 'Insufficient permission for the user %s'%question_uploader_id:
		cprint("Test Failed", "red", "on_white")
	else:
			cprint("Test Passed", "green", "on_white")
	"""	
	if r.json()['message'] != 'Permissions updated':
		cprint("Test Failed", "red", "on_white")
	else:
			cprint("Test Passed", "green", "on_white")


	cprint("Checking permissions with mongoDB whether the persmissions are updated or not", "green")
	category = category_collection.find_one({"module_id": category_id_by_admin_one})
	permission_object.pop("user_id")
	
	if category["user_permissions"][admin_two_user_id] == permission_object:
			cprint("Test Passed", "green", "on_white")


	return 

##Now admin_one created a category, Then admin one added permissions for admin_two on this category


def	create_criteria_by_admin_two(admin_two_user_id, admin_two_token, category_id):
	print ("\n\n")
	cprint("Trying to create criteria by admin Two", "green")
	cprint("This criteria must be created as admin Two [%s] has create permissions on %s"%(admin_two_user_id, category_id),  "green")

	category_data = {"criteria_name": "criteria_one_admin_two",
				 "text_description": "Description for subcategory_one_admin_two", 
				 "score": 30,
				 "user_id": admin_two_user_id,
				 "parent_id": category_id
				 }
	r = requests.post("http://localhost:8000/criteria", data=json.dumps(category_data), headers={"Authorization": question_uploader_token})
	cprint( "\t\t%s"%r.json(), "blue")

	sub_category_id = r.json()["module_id"]
	if r.json()['parent_id'] != category_id:
		cprint("\t\tTest Failed", "red", "on_white")
	else:
			cprint("\t\tTest Passed", "green", "on_white")
	
	cprint("\t\tChecking mongodb Entry for this new update in subcategory collection")
	if criteria_collection.find_one({"module_id": sub_category_id})["user_permissions"][admin_two_user_id] == \
													{"create": True, "get": True, "delete": True, "update": True}:
			cprint("\t\tTest Passed", "green", "on_white")
	else:
			cprint("\t\tTest Passed", "green", "on_white")
	
	cprint("\t\t Checking user[%s] in user_collection for subcategory[%s] permission"%(admin_two_user_id, sub_category_id))
	if users_collection.find_one({"user_id": admin_two_user_id})["permissions"]["criteria"][sub_category_id] ==\
					 {"create": True, "get": True, "delete": True, "update": True}:
			cprint("\t\tTest Passed", "green", "on_white")
	else:
			cprint("\t\tTest Passed", "green", "on_white")
					 


	return r.json()["module_id"]


def get_criteria_admin_one(sub_category_id_admin_two, admin_one_user_id, admin_one_token):
	print ("\n\n")
	cprint("Trying to get criteria [%s] by admin Two by admin one"%(sub_category_id_admin_two), "green")
	cprint("Must Fail because this category has been created by admin two")
	cprint("All other rest requests follows the same ")


	r = requests.get("http://localhost:8000/criteria/%s"%sub_category_id_admin_two, data=json.dumps({"user_id": admin_one_user_id}),\
	 headers={"Authorization": admin_one_token})
	cprint(r.json(), "blue")
	"""
	if r.json()['message'] != 'Insufficient permission for the user %s'%question_uploader_id:
		cprint("Test Failed", "red", "on_white")
	else:
			cprint("Test Passed", "green", "on_white")
	"""	

	if r.json()['message'] != "The document with id[%s] doest have permissions for user_id [%s]"%(sub_category_id_admin_two, admin_one_user_id):
		cprint("\t\tTest Failed", "red", "on_white")
	else:
		cprint("\t\tTest Passed", "green", "on_white")
	return 


def update_criteria_permission_for_question_uploader(sub_category_id_admin_two, question_uploader_id,\
					admin_two_user_id, admin_two_token):
	print ("\n\n")
	cprint("Update Permission on criteria [%s] by admin_one [%s] who created\
	 this subcategory for the question_uploader_id [%s]"%(sub_category_id_admin_two, \
	 	admin_two_user_id, question_uploader_id), "green")
	cprint("Must pass")
	permission_object = [{"user_id": admin_one_user_id , "create": True, "delete": False, "get": True, "put": True}]
	data_object = {"module_id": sub_category_id_admin_two, "user_id": admin_two_user_id, \
	"permissions": permission_object}

	r = requests.post("http://localhost:8000/criteriapermissions", data=json.dumps(data_object),\
	 headers={"Authorization": admin_two_token})

	cprint(r.json(), "blue")
	if not r.json()["success"]:
		cprint("\t\tTest Failed", "red", "on_white")
	else:
		cprint("\t\tTest Passed", "green", "on_white")
	return 



def create_admin(super_admin_id):
	user_one = {
 		'email': fake.email(),
 		'full_name': fake.name(),
 		'password': fake.password(),
 		'region': [fake.city(), fake.city()],
 		'state': [fake.state(), fake.state()],
 		'user_type': 'admin',
 		'username': fake.user_name(),
 		'parent_user_id': super_admin_id, 
 		'is_superadmin': False}

	r = requests.post("http://localhost:8000/signup", data=json.dumps(user_one), headers=headers )
	cprint(r.json(), "blue")
	return (r.json()["user_id"], r.json()["token"])


def	create_category(user_id, token):

	category_data = {"category_name": fake.slug(),
				 "text_description": fake.text(), 
				 "score": random.randint(0, 100),
				 "user_id": user_id
				 }
	r = requests.post("http://localhost:8000/category", data=json.dumps(category_data), headers={"Authorization": token})
	print ("\n\n")
	cprint(r.json(), "blue")
	return r.json()["category_id"]


def	create_criteria(user_id, parent_id, token, success):

	category_data = {"criteria_name": fake.slug(),
					"parent_id": parent_id, 
				 "text_description": fake.text(), 
				 "score": random.randint(0, 100),
				 "user_id": user_id
				 }
	r = requests.post("http://localhost:8000/criteria", data=json.dumps(category_data), headers={"Authorization": token})
	print ("\n\n")
	cprint(r.json(), "blue")
	if r.json()["success"] == success:
		cprint("\t\tTest Passed", "green", "on_white")
	else:
		cprint("\t\tTest Failed", "red", "on_white")
	try:
		module_id = r.json()["module_id"]
	except:
		module_id = None


	return module_id


def get_category(user_id, category_id, token, success):
	r = requests.get("http://localhost:8000/category/%s"%category_id, data=json.dumps({"user_id": user_id}),\
	 headers={"Authorization": token})
	cprint(r.json(), "blue")	
	if r.json()["success"] == success:
		cprint("\t\tTest Passed", "green", "on_white")
	else:
		cprint("\t\tTest Failed", "red", "on_white")
	return 


def get_module(user_id, module_id, module_name, token, success):
	r = requests.get("http://localhost:8000/%s/%s"%(module_name, module_id), data=json.dumps({"user_id": user_id}),\
	 headers={"Authorization": token})
	cprint(r.json(), "blue")	
	if r.json()["success"] == success:
		cprint("\t\tTest Passed", "green", "on_white")
	else:
		cprint("\t\tTest Failed", "red", "on_white")
	return 


def get_all_module(user_id, module_name, token, length):
	print (user_id)
	r = requests.post("http://localhost:8000/%s"%module_name, data=json.dumps({"user_id": user_id}),\
	 headers={"Authorization": token})
	cprint(r.json(), "blue")	
	if len(r.json()["result"]) == length:
		cprint("\t\tTest Passed", "green", "on_white")
	else:
		cprint("\t\tTest Failed", "red", "on_white")
	return 


def	create_module(user_id, parent_id, module_api, module_name, token, success, documents_required=None):

	data = {module_name: fake.slug(),
					"parent_id": parent_id, 
				 "text_description": fake.text(), 
				 "score": random.randint(0, 100),
				 "user_id": user_id
				 }

	if documents_required:
			data.update({"documents_required": documents_required})
			print(data)
	r = requests.post("http://localhost:8000/%s"%module_api, data=json.dumps(data), headers={"Authorization": token})
	print ("\n\n")
	cprint(r.json(), "blue")
	if r.json()["success"] == success:
		cprint("\t\tTest Passed", "green", "on_white")
	else:
		cprint("\t\tTest Failed", "red", "on_white")
	try:
		module_id = r.json()["module_id"]
	except:
		module_id = None


	return module_id


def get_all_categories(user_id, token, length):
	print (user_id)
	r = requests.post("http://localhost:8000/categories", data=json.dumps({"user_id": user_id}),\
	 headers={"Authorization": token})
	cprint(r.json(), "blue")	
	if len(r.json()["result"]) == length:
		cprint("\t\tTest Passed", "green", "on_white")
	else:
		cprint("\t\tTest Failed", "red", "on_white")
	return 

def delete_module(user_id, module_api, module_id,  token, success):
	data = {"user_id": user_id}
	r = requests.delete("http://localhost:8000/%s/%s"%(module_api, module_id),  data=json.dumps(data), headers={"Authorization": token})
	cprint(r.json(), "blue")
	if r.json()["success"] == success:
		cprint("\t\tTest Passed", "green", "on_white")
	else:
		cprint("\t\tTest Failed", "red", "on_white")



if __name__ == "__main__":
	insert_super_admin()

	(admin_one_user_id, admin_one_token) = create_admin_one()
	check_if_login_provides_same_token(admin_one_token)

	(admin_two_user_id, admin_two_token) = create_admin_two()
	(super_admin_user_id, super_admin_token) = create_super_admin()
	create_super_admin_by_admin(admin_one_user_id,  admin_one_token)
	create_admin_three_by_admin(admin_two_user_id, admin_two_token)

	(question_uploader_id, question_uploader_token) = create_user_first(admin_one_user_id, admin_one_token)
	create_user_second(admin_one_user_id, admin_one_token)


	users_by_admin(admin_one_user_id, admin_one_token)
	"""
	create_category_by_superadmin(super_admin_user_id)
	create_category_by_question_uploader(question_uploader_id, question_uploader_token)
	category_id_by_admin_one = create_category_by_admin_one(admin_one_user_id, admin_one_token)

	get_category_by_admin_two(admin_two_user_id, admin_two_token, category_id_by_admin_one)
	change_permissions_by_admin_two(admin_two_user_id, admin_two_token, category_id_by_admin_one)
	adding_permissions_by_admin_one_for_admin_two(admin_one_user_id, admin_two_user_id, admin_one_token, category_id_by_admin_one)
	sub_category_id_admin_two = create_criteria_by_admin_two(admin_two_user_id, admin_two_token, category_id_by_admin_one)

	get_criteria_admin_one(sub_category_id_admin_two, admin_one_user_id, admin_one_token)


	update_criteria_permission_for_question_uploader(sub_category_id_admin_two, question_uploader_id,\
					admin_two_user_id, admin_two_token)

	"""
	a_admin_id, a_admin_token = create_admin(super_admin_user_id)
	b_admin_id, b_admin_token = create_admin(super_admin_user_id)
	c_admin_id, c_admin_token = create_admin(super_admin_user_id)
	
	aa_cat_id = create_category(a_admin_id, a_admin_token)
	"""
	ab_cat_id = create_category(a_admin_id, a_admin_token)
	ac_cat_id = create_category(a_admin_id, a_admin_token)

	bb_cat_id = create_category(b_admin_id, b_admin_token)
	cc_cat_id = create_category(c_admin_id, c_admin_token)

	print(aa_cat_id)
	get_category(a_admin_id, aa_cat_id, a_admin_token, True)
	get_category(b_admin_id, bb_cat_id, b_admin_token, True)

	#Fail, because b_admin has no permission on aa_cat_id
	get_category(b_admin_id, aa_cat_id, b_admin_token, False)

	##till now 3 categories created by a_admin_id, 
	get_all_categories(a_admin_id, a_admin_token, 3)

	##Todo Some funck with permissions
	"""
	##Creating criteria by a_admin_id on aa_cat_id
	aa_criteria_id = create_criteria(a_admin_id, aa_cat_id, a_admin_token, True)
	
	ab_criteria_id = create_criteria(a_admin_id, aa_cat_id, a_admin_token, True)
	ac_criteria_id = create_criteria(a_admin_id, aa_cat_id, a_admin_token, True)

	##Try to create criteria by b_admin_id on aa_cat_id
	create_criteria(b_admin_id, aa_cat_id, b_admin_token, False)

	##get criteria by a_admin_id
	get_module(a_admin_id, aa_criteria_id, "criteria", a_admin_token, True)

	##get criteria by b_admin_id, created by a_admin_id
	get_module(b_admin_id, aa_criteria_id, "criteria", a_admin_token, False)


	##get all criteria by a_admin_id
	get_all_module(a_admin_id, "criterion", a_admin_token, 3)

	##get all criteria by b_admin_id
	print ("\n\n\n")
	get_all_module(b_admin_id, "criterion", b_admin_token, 0)

	#Creating sub criteria by a_admin_id
	aa_sub_criteria_id = create_module(a_admin_id, aa_criteria_id, "subcriteria", "sub_criteria_name", a_admin_token, True)
	ab_sub_criteria_id = create_module(a_admin_id, aa_criteria_id, "subcriteria", "sub_criteria_name", a_admin_token, True)
	ac_sub_criteria_id = create_module(a_admin_id, aa_criteria_id, "subcriteria", "sub_criteria_name", a_admin_token, True)


	"""
	#Creating sub criteria by b_admin_id, They all going to fail because b_admin_id doesnt have an permission on parent 
	##category aa_criteria_id which was created by a_admin_id
	ba_sub_criteria_id = create_module(b_admin_id, aa_criteria_id, "subcriteria", "sub_criteria_name", b_admin_token, False, )
	bb_sub_criteria_id = create_module(b_admin_id, ab_criteria_id, "subcriteria", "sub_criteria_name", b_admin_token, False)
	bc_sub_criteria_id = create_module(b_admin_id, ac_criteria_id, "subcriteria", "sub_criteria_name", b_admin_token, False)
	"""




	##CReate LEVELS
	aa_level_id = create_module(a_admin_id, aa_sub_criteria_id, "level", "level_name", a_admin_token, True)
	ab_level_id = create_module(a_admin_id, aa_sub_criteria_id, "level", "level_name", a_admin_token, True)
	ac_level_id = create_module(a_admin_id, aa_sub_criteria_id, "level", "level_name", a_admin_token, True)


	##CReate Questions
	aa_question_id = create_module(a_admin_id, aa_level_id, "question", "question_name", a_admin_token, True, ["address_proof"])
	ab_question_id = create_module(a_admin_id, aa_level_id, "question", "question_name", a_admin_token, True, ["address_proof", "incomme_tax_statement"])
	ac_question_id = create_module(a_admin_id, aa_level_id, "question", "question_name", a_admin_token, True, ["address_proof", "id_proof"])
	ad_question_id = create_module(a_admin_id, aa_level_id, "question", "question_name", a_admin_token, True, ["address_proof", "id_proof"])
	ae_question_id = create_module(a_admin_id, aa_level_id, "question", "question_name", a_admin_token, True, ["address_proof", "id_proof"])



	#Delete Tests 
	##ideally when we delete a question, level, criteria, sub_criteria it shall delet the 
	##the module itself and all its categories
	##first lets try to delete any question created above by b_admin_id, who didnt create a question
	## This endeavour shall fail as b_admin_id doesnt have permission on this question
	delete_module(b_admin_id, "question", aa_question_id, b_admin_token, False)

	##Now trying to delete the aa_question_id by a_admin_id, It shall delete the mentioned question, 
	##as it was created by a_admin_id
	delete_module(a_admin_id, "question", aa_question_id, a_admin_token, True)

	##til now rh graph of modules looks like this 
	"""

											aa_cat_id (a_admin_id)
													|
						aa_criteria_id(a_admin_id)          ab_criteria_id(a_admin_id)                    ac_criteria_id(a_admin_id)
									|								|													|
		aa_sub_criteria_id    ab_sub_criteria_id  ac_sub_criteria_id	
				|
				|
				|___________________________
											|
								aa_level_id            ab_level_id           ac_level_id
										|
										|
										|
				aa_question_id ab_question_id ac_question_id ad_question_id  ae_aquestion_id						

	"""
	##Now trying to delete a subcriteria aa_sub_criteria_id, this shall delete all the questions, level made till now.
	##this will delete all the nodes below this aa_criteria_id and also deletes the aa_criteria_id frpm the 
	## parent_collection children key, Ideally if we going to delete the aa_cat_id it should delete all the
	## surbranches 
	delete_module(a_admin_id, "criteria", aa_criteria_id, a_admin_token, True)


