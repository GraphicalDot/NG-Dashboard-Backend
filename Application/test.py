
import requests
import json
import pprint
import pymongo

app_super_admin = "nctsuperadmin"
app_super_admin_pwd = "1234Pacific###"
app_port = 8000
mongo_user = "application"
mongo_pwd = "1234Pacific###"
mongo_ip = "localhost"
mongo_port = 27017
category_collection_name = "categories"
sub_category_collection_name = "subcategories"
level_collection_name = "levels"



uri = "mongodb://%s:%s@%s:%s/%s"%(mongo_user, mongo_pwd, mongo_ip, mongo_port, "admin")
print (uri)
client = pymongo.MongoClient(uri)
client.drop_database("tiapplication")
db = client["tiapplication"]

category_collection = db[category_collection_name]

##adding user_id=="superadmin" to categiry collection
db[category_collection_name].update_one({"name": "super_permissions"},  {"$addToSet": { "all": "superadmin"}}, upsert=True)
db[sub_category_collection_name].update_one({"name": "super_permissions"},  {"$addToSet": { "all": "superadmin"}}, upsert=True)
db[level_collection_name].update_one({"name": "super_permissions"},  {"$addToSet": { "all": "superadmin"}}, upsert=True)


user_one = {
 'email': 'shivaanipahuja@gmail.com',
 'full_name': 'shikha kaur',
 'password': 'merijaanshikha',
 'region': ['delhi', 'mumbai'],
 'state': ['delhi', 'mumbai'],
 'user_type': 'accessor',
 'username': 'shikha'}


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


headers = {"Authorization": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJwYXNzd29yZCI6IjEyMzRQYWNpZmljIyMjIiwidXNlcl90eXBlIjoic3VwZXJhZG1pbiIsInVzZXJuYW1lIjoibmN0c3VwZXJhZG1pbiJ9.ZSCDjXx_n5LpkJAkzyKFke0ovax-zb6pps1SiFEKosA"}

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

