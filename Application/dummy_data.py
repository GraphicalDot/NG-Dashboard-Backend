
#!/usr/bin/env python
import requests
import json
from faker import Faker
from pprint import pprint
import random
fake = Faker()


root_url = "http://localhost:8000/"

class Generate(object):
        def __init__(self, number, url_extension, object_id_name, user_id=None, user_name=None, 
                    parent_id=None, parent_name=None, connections=None, bloom_taxonomy=None,
                     difficulty_level=None, required_domains=None):
            self.number = number
            self.url_extension = url_extension
            self.object = []
            self.object_id_name = object_id_name
            self.object_ids = []
            self.user_id = user_id
            self.user_name = user_name
            self.parent_id = parent_id
            self.parent_name = parent_name
            self.connections = connections
            self.bloom_taxonomy = bloom_taxonomy
            self.difficulty_level = difficulty_level
            self.required_domains = required_domains

            self.post_request()
            pprint(self.fetch_all_data())
            return 

        def post_request(self):
            for i in range(0, self.number):
                    response = requests.post("%s%s"%(root_url, self.url_extension), data=self.data())
                    self.object.append(response.json()["data"])
                    self.object_ids.append(response.json()["data"][self.object_id_name])

        def data(self):
            return None

        def fetch_all_data(self):
            response = requests.get("%s%s"%(root_url, self.url_extension))
            return response.json()["data"]

class GenerateUser(Generate):            
        def data(self):
                dump = json.dumps({"first_name": fake.first_name(),
                            "last_name": fake.last_name(),
                            "email": fake.email(),
                            "password": fake.password(),
                            "is_admin": False, 
                            "user_type": "superadmin",
                            "phone_number": fake.phone_number(), 
                            "user_name": fake.user_name()})
                return dump



class GenerateDomains(Generate):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def data(self):
                dump = json.dumps({"domain_name": fake.slug(),
                         "description": fake.paragraph(),
                          "user_type": "superadmin", 
                          "user_id": self.user_id, 
                          "user_name": self.user_name})
                return dump


class GenerateConcepts(Generate):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def data(self):
                dump = json.dumps({"concept_name": fake.slug(),
                         "description": fake.paragraph(),
                          "user_type": "superadmin", 
                          "user_id": self.user_id, 
                          "user_name": self.user_name, 
                          "parent_id": self.parent_id, 
                          "parent_name": self.parent_name,
                          "connections": self.connections,
                          "bloom_taxonomy": self.bloom_taxonomy, 
                          "difficulty_level": self.difficulty_level, 
                          "required_domains": self.required_domains  
                          })
                return dump


users = GenerateUser(5, "users", "user_id", "asa344", "kaali")
user_ids = users.object_ids
user_list = users.object

domains = GenerateDomains(5, "domains", "domain_id", user_id=user_list[0].get("user_id"), user_name=user_list[0].get("user_name") )
domain_ids = domains.object_ids
domain_list = domains.object

##TODO: make changes to somehow randomise parent_id and parent_name
concepts = GenerateConcepts(5, "concepts", "concept_id", user_id=user_list[0].get("user_id"), user_name=user_list[0].get("user_name"), 
                                parent_id=domain_list[0].get("domain_id"), parent_name=domain_list[0].get("domain_name"), 
                                connections= [],  bloom_taxonomy=["A", "B", "C"],
                                difficulty_level=random.randint(1, 10),  
                                required_domains= random.sample([_.get("domain_name") for _ in domain_list], random.randint(1, 4))
                                )
concepts.object
concepts.object_ids



"""

concepts = GenerateDomains(5, "domains", "domain_id", user_list[0].get("user_id"), user_list[0].get("user_name") )
domains.object
domains.object_ids

user_one_id = requests.post("%susers"%root_url, data=user_data())
user_two_id = requests.post("%susers"%root_url, data=user_data())
user_third_id = requests.post("%susers"%root_url, data=user_data())
user_fourth_id = requests.post("%susers"%root_url, data=user_data())

print ("First user_id created <<%s>>"%user_one_id.json()["data"]["user_id"])
print ("Second user_id created <<%s>>"%user_two_id.json()["data"]["user_id"])
print ("Third user_id created <<%s>>"%user_third_id.json()["data"]["user_id"])
print ("Foruth user_id created <<%s>>"%user_fourth_id.json()["data"]["user_id"])

#Get all users data
user_data = requests.get("%susers"%root_url)
pprint (user_data["data"])

domain_one = requests.post("%sdomains"%root_url, data=domain_data())
domain_two = requests.post("%sdomains"%root_url, data=domain_data())
domain_three= requests.post("%sdomains"%root_url, data=domain_data())
domain_four = requests.post("%sdomains"%root_url, data=domain_data())
pprint (domain_one["data"])
pprint (domain_one["data"])
pprint (domain_one["data"])
pprint (domain_one["data"])
"""



