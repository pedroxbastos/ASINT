from flask import Flask
from flask import jsonify
from flask import request
from pymongo import MongoClient, errors
import pprint
import json
import fenixedu
from math import radians, cos, sin, asin, sqrt
import datetime



Messages = {}

#logs = {}

#def addLog(name,Location):
#	logs.update({name:Location})

app = Flask(__name__)
client = MongoClient('mongodb://pedroxbastos:Pb9127416716@ds025180.mlab.com:25180/asint')
db = client['asint']


@app.route('/')
def hello_world():
	return 'Hello World!'

#  Admin API
@app.route('/API/Admin/GetBuildsLocations', methods=['POST'])
def BuildsLocations():
	if request.method == "POST":
		content = request.json
		#  content -> string
		content2 = json.loads(content.replace("'","\""))
		#  content -> list of dict
		collection = db[content2[0]['campus']]
		i=1
		err=0
		#  insert one by one and count errors
		while i<= (len(content2)-1):
			try:
				if content2[0]['campus'] in content2[i]['campus'].lower():
					collection.insert_one(content2[i])
					print("ok")
			except errors.DuplicateKeyError:
				err= err +1
			i=i+1
		return jsonify("%d insertions were made" % (len(content2)-1 - err))

@app.route('/API/Admin/GetBuildingList', methods=['POST'])
def BuildingList():
	if request.method == "POST":
		content = request.json
		print(content)
		collection = db[content['campus']]
		ret = []
		for c in collection.find({},{'_id': False}):
			ret.append(c)
		print(type(ret))
		return json.dumps(str(ret))

@app.route('/API/Admin/GetListAllUsersLogged', methods=['POST'])
def ListUsersLogged():
		#  Ver sessions e perguntar aos outros servidores por users em sessions também.
	return jsonify( {"aaa":12, "bbb": ["bbb", 12, 12] })


@app.route('/API/Admin/GetListAllUsersInBuild', methods=['POST'])
def ListUsersInsideB():
	if request.method == "POST":
		content = request.json
		building_id = content['building_id']
		campus = content['campus']
		collection = db[campus]
		if collection.count_documents({"id" : building_id}) ==0:
			return json.dumps("The given building ID does not exist in campus %s." % campus)
		else:
			ret = []
			collection = db["logs"]
			for c in collection.find({"type" : "move", "building" : building_id, "checkout" : "0"},{'_id': False}):
				ret.append(c['user'])
				print(type(ret))
			if len(ret) == 0:
				return json.dumps("There are no users currently in the given building.")
			else:
				return json.dumps(str(ret))


@app.route('/API/Admin/GetListHistory', methods=['POST'])
def getUserHistory():
	if request.method == "POST":
		content = request.json
		userID = content['userID']
		print(userID)
		collection = db["logs"]
		if collection.count_documents({"userID" : userID}):
			return json.dumps("The are no logs for user %s." % userID)
		else:
			ret = []
			for c in collection.find({"$or":[ {"user":userID}, {"to":userID}, {"from_":userID}]}, {'_id':False}).sort('date',1):
				print(c)
				ret.append(c)
			return json.dumps(str(ret))

@app.route('/API/insert', methods=['POST'])
def addLog():
	content=request.json
	content2 = json.loads(content.replace("'", "\""))
	collection = db["logs"]
	c = collection.insert_one(content2)
	return json.dumps("ok")



#  User API
"""@app.route('/API/User/init', methods=['POST'])
def redirectURLforuser():
	#para receber o token do user (ainda nao funciona)
	config = fenixedu.FenixEduConfiguration('1977390058176578', 'http://127.0.0.1:5002/User/Mainpage', 'XUwJJfct3cBy7jBbS+NOQVqrQ1eQGN1F9kYAWI3MCMpxgG/J4+h3Qv9+GmOS0Fs+F+Aml8kkZVXroJIb8SZyRw==', 'https://fenix.tecnico.ulisboa.pt/')
	client = fenixedu.FenixEduClient(config)
	url = client.get_authentication_url()
	return jsonify({'url': url})"""


@app.route('/API/User/Tokencode', methods=['POST'])
def getUtoken():
	config = fenixedu.FenixEduConfiguration('1695915081465925', 'http://127.0.0.1:5002/User/Mainpage', 'd/USUpUYU7o20hWNwEi+S3PWW5Cc4ypiQrX3rUfxLAcFat0epdCuxjS35iIWNwJ4ruCu9D7bL2GXZc9P4RDNvQ==', 'https://fenix.tecnico.ulisboa.pt/')
	client = fenixedu.FenixEduClient(config)
	content = request.get_json()
	user = client.get_user_by_code(str(content["code"]).split('=')[1])
	person = client.get_person(user)
	return jsonify( [{"result": "Token successfull"}] )



@app.route('/API/User/PostmyLocation', methods=['POST'])
def PostmyLocal():
	#User envia localizaçao e nome e atualiza. Isto depois deve atualizar na BD
	collection = db.logs
	content = request.get_json()
	print(content)
	print(content["name"])
	localisation={"Latitude": content["location"][0], "Longitude":content["location"][1]}
	for obj in collection.find({"name": content["name"]}):
		collection.update_one({"name": content["name"]}, {"$set": {"localisation": localisation}})
		pprint.pprint(obj)
		break
	return jsonify( [{"result": "Logs updated"}] )

@app.route('/API/User/SendBroadMsg', methods=['POST'])
def SendMsg():
	collection = db.logs
	content = request.get_json()
	objself=None
	for obj in collection.find({"name": content["name"]}):
		objself=obj
		break
	for obj in collection.find():
		if obj != objself:
			if obj["name"] in Messages:
				Messages[obj["name"]].append(content["Message"])
			else:
				Messages[obj["name"]]= []
				Messages[obj["name"]].append(content["Message"])
	print(Messages)
	return jsonify( {"aaa":12, "bbb": ["bbb", 12, 12] })

@app.route('/API/User/DefineDistance', methods=['POST'])
def DefineRange():
	return jsonify( {"aaa":12, "bbb": ["bbb", 12, 12] })

@app.route('/API/User/RecvMsg', methods=['GET'])
def RecvMsg():
	return jsonify( {"aaa":12, "bbb": ["bbb", 12, 12] })


# Bots API

# Other Servers API
# Vai ser preciso para quando uns users estão logged num server e outros noutros e é preciso procurar todos.

#Outros

def calculateDistance(b_lat, b_long, u_lat, u_long):
	#  30m range; haversine formula.
	b_lat, b_long, u_lat, u_long = map(radians, [b_lat, b_long, u_lat, u_long])
	dlon = b_long - u_long
	dlat = b_lat - u_lat
	a = sin(dlat / 2) ** 2 + cos(b_lat) * cos(u_lat) * sin(dlon / 2) ** 2
	c = 2 * asin(sqrt(a))
	r = 6371 * 1000  # Radius of earth in meters.
	if c*r >=30:
		return False
	else:
		return True


if __name__ == '__main__':
	app.run()
