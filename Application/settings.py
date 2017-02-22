
import motor
from datetime import datetime
from pytz import timezone    

mongo_user = "application"
mongo_pwd = "1234Pacific###"
mongo_ip = "localhost"
mongo_port = 27017
mongo_db_name = "tiapplication"
credential_collection_name = "credentials"
accessor_collection_name  = "accessor"
admin_collection_name = "admin"
superadmin_collection_name = "superadmin"
evaluator_collection_name = "evaluators"
jwt_secret = "somesecret"
app_super_admin = "nctsuperadmin"
app_super_admin_pwd = "1234Pacific###"

#uri = "mongodb://user:pass@localhost:27017/database_name"
uri = "mongodb://%s:%s@%s:%s/%s"%(mongo_user, mongo_pwd, mongo_ip, mongo_port, "admin")
#mongo_db = motor.motor_tornado.MotorClient(uri)
client = motor.motor_tornado.MotorClient(uri)
mongo_db = client[mongo_db_name]
# For connecting to replication set 
#mongo_client = motor.motor_tornado.MotorClient('mongodb://host1,host2/?replicaSet=my-replicaset-name')


TIME_ZONE =  'Asia/Kolkata'

def indian_time():
	india  = timezone(TIME_ZONE)
	n_time = datetime.now(india)
	return n_time.strftime('%Y-%m-%d %H-%M-%s')
