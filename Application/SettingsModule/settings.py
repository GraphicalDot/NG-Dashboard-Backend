
import motor
from datetime import datetime
from pytz import timezone    
import os
app_port = 8000
mongo_user = "application"
mongo_pwd = "1234Pacific###"
mongo_ip = "localhost"
mongo_port = 27017
mongo_db_name = "dashboard"
user_collection_name = "users"
question_types = ["multiple_choice"]

permission_collection_name = "permissions"


subject_collection_name = "subjects"
board_collection_name = "boards"
domain_collection_name = "domains"
concept_collection_name = "concepts"
subconcept_collection_name = "subconcepts"
nanoskill_collection_name = "nanoskills"
question_collection_name = "questions"
action_collection_name = "actions"
image_collection_name = "images"
template_collection_name = "templates"

jwt_secret = "HelloOfAkind###"
app_super_admin = "nctsuperadmin"
app_super_admin_pwd = "1234Pacific###"
app_super_admin_user_id = "nctsuperadmin###"




os.environ['S3_USE_SIGV4'] = 'True'
bucket_name = "newunlearnimages"
access_key_id = "AKIAJHUY754DHIT5ZNQQ"
secret_access_key = "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"
host= "s3.ap-south-1.amazonaws.com"

import boto3
from botocore.client import Config

s3connection = boto3.client(
    's3',
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key,
	config=Config(signature_version='s3v4'), 
	region_name="ap-south-1"
)

#s3connection = boto.connect_s3(access_key_id, secret_access_key, host=host)


##change this if you want all get requests for list to return more than 10 results
default_document_limit = 10

#uri = "mongodb://user:pass@localhost:27017/database_name"
uri = "mongodb://%s:%s@%s:%s/%s"%(mongo_user, mongo_pwd, mongo_ip, mongo_port, "admin")
#mongo_db = motor.motor_tornado.MotorClient(uri)
client = motor.motor_tornado.MotorClient(uri)
db = client[mongo_db_name]
mongo_db = db
  
credentials_collection = db["credentials"]
# For connecting to replication set 
#mongo_client = motor.motor_tornado.MotorClient('mongodb://host1,host2/?replicaSet=my-replicaset-name')


TIME_ZONE =  'Asia/Kolkata'


permissions = {"ids": [], "super": False}




def indian_time():
	india  = timezone(TIME_ZONE)
	n_time = datetime.now(india)
	#return n_time.strftime('%Y-%m-%d %H-%M-%s')
	return n_time.strftime("%b %d %Y %H:%M:%S")
