
import requests
import json
import pprint
import pymongo
from termcolor import colored, cprint

app_super_admin = "nctsuperadmin"
app_super_admin_pwd = "1234Pacific###"
app_super_admin_user_id = "nctsuperadmin###"
app_port = 8000
mongo_user = "application"
mongo_pwd = "1234Pacific###"
mongo_ip = "localhost"
mongo_port = 27017
category_collection_name = "categories"
sub_category_collection_name = "subcategories"
level_collection_name = "levels"
user_collection_name = "users"


uri = "mongodb://%s:%s@%s:%s/%s"%(mongo_user, mongo_pwd, mongo_ip, mongo_port, "admin")
print (uri)
client = pymongo.MongoClient(uri)
client.drop_database("tiapplication")
db = client["tiapplication"]

category_collection = db[category_collection_name]


##adding user_id=="superadmin" to categiry collection
#db[user_collection_name].update_one({"name": "super_permissions"},  {"$addToSet": { "all": "superadmin"}}, upsert=True)
#db[sub_category_collection_name].update_one({"name": "super_permissions"},  {"$addToSet": { "all": "superadmin"}}, upsert=True)
#db[level_collection_name].update_one({"name": "super_permissions"},  {"$addToSet": { "all": "superadmin"}}, upsert=True)

address = "http://localhost:8000"


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
	cprint("Trying to create category by admin one", "green")

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

	r = requests.post("http://localhost:8000/categorypermissions", data=json.dumps(data_object),\
	 headers={"Authorization": admin_two_token})

	print (r.text)
	"""
	if r.json()['message'] != 'Insufficient permission for the user %s'%question_uploader_id:
		cprint("Test Failed", "red", "on_white")
	else:
			cprint("Test Passed", "green", "on_white")
	if r.json()['message'] != 'Insufficient permission for the user %s'%admin_two_user_id:
		cprint("Test Failed", "red", "on_white")
	else:
			cprint("Test Passed", "green", "on_white")
	return 
	"""	



def	adding_permissions_by_admin_one_for_admin_two(admin_one_user_id, admin_two_user_id, admin_one_token, category_id_by_admin_one):
	print ("\n\n")
	cprint("Till now category_id [%s] which was created by admin one [%s] doiesnt have permissions\
	 for admin two[%s]"%(category_id_by_admin_one, admin_one_user_id, admin_two_user_id), "green")
	data_object = {"category_id": category_id_by_admin_one, "user_id": admin_one_user_id, \
	"permissions": [{"user_id": admin_two_user_id , "create": True, "delete": False, "get": True, "put": True}]}

	r = requests.post("http://localhost:8000/categorypermissions", data=json.dumps(data_object),\
	 headers={"Authorization": admin_two_token})

	print (r.text)
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
	"""
	for user in db[user_collection_name].find():
		pprint.pprint (user)
		print("\n\n")
	"""
	users_by_admin(admin_one_user_id, admin_one_token)
	create_category_by_superadmin(super_admin_user_id)
	create_category_by_question_uploader(question_uploader_id, question_uploader_token)
	category_id_by_admin_one = create_category_by_admin_one(admin_one_user_id, admin_one_token)
	get_category_by_admin_two(admin_one_user_id, admin_one_token, category_id_by_admin_one)
	change_permissions_by_admin_two(admin_two_user_id, admin_two_token, category_id_by_admin_one)
	adding_permissions_by_admin_one_for_admin_two(admin_one_user_id, admin_two_user_id, admin_one_token, category_id_by_admin_one)


"""

def create_admin_one():
	cprint("creating first admin by super admin", "green")
	user_one = {
 		'email': 'adminone@gmail.com',
 		'full_name': 'admin one',
 		'password': 'passwordone',
 		'region': ['delhi', 'mumbai'],
 		'state': ['delhi', 'mumbai'],
 		'user_type': 'admin',
 		'username': 'adminone',
 		'parent_id': app_super_admin_user_id, 
 		'is_superadmin': False}

	r = requests.post("http://localhost:8000/signup", data=json.dumps(user_one), headers=headers )
	pprint.pprint(r.json())
	return (r.json()["user_id"], r.json()["token"])

user_two = {
 'email': 'houzier.saurav@gmail.com',
 'full_name': 'saurav verma',
 'password': '12345',
 'region': ['chandigram', 'rajasthan'],
 'state': ['delhi', 'mumbai'],
 'user_type': 'admin',
 'username': 'kaali'}


user_three = {'category_permissions': {'ids': [], 'super': True},
 'email': 'vikram.jindal@gmail.com',
 'full_name': 'vikram jindal',
 'password': '12345',
 'region': ['kerela', 'maharashtra'],
 'state': ['delhi', 'noida', "dwarka"],
 'user_type': 'admin',
 'username': 'vikram', 
 "category_permissions": {"ids": [], "super": True}}



r = requests.post("http://localhost:8000/signup", data=json.dumps(user_one), headers=headers )
pprint.pprint(r.json())

r = requests.post("http://localhost:8000/signup", data=json.dumps(user_two), headers=headers )
pprint.pprint(r.json())

r = requests.post("http://localhost:8000/signup", data=json.dumps(user_three), headers=headers )
pprint.pprint(r.json())



r = requests.post("http://localhost:8000/login", data=json.dumps(user_two), headers=headers )
response_one= r.json()
pprint.pprint(r.json())


r = requests.post("http://localhost:8000/login", data=json.dumps(user_two), headers=headers )
response_two = r.json()
pprint.pprint(r.json())


r = requests.post("http://localhost:8000/login", data=json.dumps(user_three), headers=headers )
response_three = r.json()
pprint.pprint(r.json())


print ("\n\n")

pprint.pprint(category_collection.find_one())
pprint.pprint("FROM TEST: The user id %s doesnt have permission to create category" %(response_one["user_id"]))
category_data = {"category_name": "test category one",
				 "text_description": "This is a text description for test categry one", 
				 "score": 20,
				 "user_id": response_one["user_id"]
				 }


r = requests.post("http://localhost:8000/category", data=json.dumps(category_data), headers=headers)
#response_three = r.json()
pprint.pprint(r.json())


print ("\n\n")
print("checking is user with all permission can create a category or not")
pprint.pprint("The user id %s [user_three]  have permission to create category" %(response_three["user_id"]))
category_data["user_id"] = response_three["user_id"]
r = requests.post("http://localhost:8000/category", data=json.dumps(category_data), headers=headers)
response_category = r.json()
pprint.pprint(r.json())


user_four = {
 'email': 'b@gmail.com',
 'full_name': 'bb bb',
 'password': '12345',
 'region': ['kerela', 'maharashtra'],
 'state': ['delhi', 'noida', "dwarka"],
 'user_type': 'admin',
 'username': 'bb', 
 }

r = requests.post("http://localhost:8000/signup", data=json.dumps(user_four), headers=headers )
r = requests.post("http://localhost:8000/login", data=json.dumps(user_four), headers=headers )
response_four= r.json()
pprint.pprint(r.json())


print ("\n\n")
print("Now providing permissions to user four by the user three to the above created category")
pprint.pprint("The user id %s [user_three]  have permission to edit category" %(response_three["user_id"]))
pprint.pprint("The user id %s [user_four]  is now being added to category permissions" %(response_four["user_id"]))

category_data["user_id"] = response_three["user_id"]
category_data["permissions"] = {"ids": [{"id": response_four["user_id"], 
										"create": True, "get": True, "update": True, "delete": False}], "super": False}
r = requests.put("http://localhost:8000/category/%s"%response_category['category_id'], data=json.dumps(category_data), headers=headers)
#response_three = r.json()
pprint.pprint(r.json())
pprint.pprint(category_collection.find_one({"category_id": response_category["category_id"]}))


print ("\n\n")
print("Now User four with user_id %s does not have permissions to delete category"%response_four["user_id"])
category_data["user_id"] = response_four["user_id"]
r = requests.delete("http://localhost:8000/category/%s"%response_category['category_id'], data=json.dumps(category_data), headers=headers)
#response_three = r.json()
pprint.pprint(r.json())



print ("\n\n")
print("User four with user id [%s] have the get permission for this category"%response_four["user_id"])
category_data["user_id"] = response_four["user_id"]
r = requests.get("http://localhost:8000/category/%s"%response_category['category_id'], data=json.dumps(category_data), headers=headers)
#response_three = r.json()
pprint.pprint(r.json())

"""