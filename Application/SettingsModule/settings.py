
import motor
from datetime import datetime
from pytz import timezone    

app_port = 8000
mongo_user = "application"
mongo_pwd = "1234Pacific###"
mongo_ip = "localhost"
mongo_port = 27017
mongo_db_name = "dashboard"
user_collection_name = "users"
nanoskill_collection_name = "nanoskills"

jwt_secret = "somesecret"
app_super_admin = "nctsuperadmin"
app_super_admin_pwd = "1234Pacific###"
app_super_admin_user_id = "nctsuperadmin###"


##change this if you want all get requests for list to return more than 10 results
default_document_limit = 10

#uri = "mongodb://user:pass@localhost:27017/database_name"
#uri = "mongodb://%s:%s@%s:%s/%s"%(mongo_user, mongo_pwd, mongo_ip, mongo_port, "admin")
#mongo_db = motor.motor_tornado.MotorClient(uri)
client = motor.motor_tornado.MotorClient()
mongo_db = client[mongo_db_name]
print(mongo_db)
credentials_collection = mongo_db["credentials"]
# For connecting to replication set 
#mongo_client = motor.motor_tornado.MotorClient('mongodb://host1,host2/?replicaSet=my-replicaset-name')


TIME_ZONE =  'Asia/Kolkata'


permissions = {"ids": [], "super": False}




def indian_time():
	india  = timezone(TIME_ZONE)
	n_time = datetime.now(india)
	return n_time.strftime('%Y-%m-%d %H-%M-%s')
