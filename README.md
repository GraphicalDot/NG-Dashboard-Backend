pyJwt Librabry
https://pypi.python.org/pypi/PyJWT/1.4.0


Install Mongdb


sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv
0C49F3730359A14518585931BC711F9BA15703C6

echo "deb [ arch=amd64,arm64 ] http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.4.list

sudo apt-get update
sudo apt-get install -y mongodb-org


sudo mongod --storageEngine wiredTiger --dbpath /var/lib/mongodb/ --fork --logpath /var/log/mongodb/mogod.log
replace dbpath with your own EBS storage volume, if any

To configure user role

use admin
db.createUser(
   {
       user: "tom", 
       pwd: "jerry", 
       roles:["root"]
   })


stop mongo instance 
start again 
sudo mongo -u "application" -p "1234Pacific###" --authenticationDatabase "admin"








 data={"state": "Delhi", "region": "malviya nagar", "user_type": "accessor",
"email": "a@gmail.com", "username": "kaali" , "password": "merijaanshikha",
"full_name": "shika kaur"}
r = requests.post("http://localhost:8000/signup", data=data)   
response: {'error': False, 'success': True, 'token': 'security'}



