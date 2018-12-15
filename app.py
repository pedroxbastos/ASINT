from flask import Flask
from flask import jsonify
from flask import request
from pymongo import MongoClient, errors
import pprint
import json


#logs = {}

#def addLog(name,Location):
#	logs.update({name:Location})

app = Flask(__name__)
client = MongoClient('mongodb://pedroxbastos:Pb9127416716@ds025180.mlab.com:25180/asint')
db = client['asint']


@app.route('/')
def hello_world():
	print(app.app_context())
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
			for c in collection.find({"type" : "move", "building_id" : building_id, "checkout" : "0"},{'_id': False}):
				ret.append(c)
				print(type(ret))
			if len(ret) == 0:
				return json.dumps("There are no users currently in the given building.")
			else:
				return json.dumps(str(ret))


@app.route('/API/Admin/GetListHistory', methods=['GET'])
def getUserHistory():
	return jsonify( {"aaa":12, "bbb": ["bbb", 12, 12] })

#  User API

@app.route('/API/User/init', methods=['POST'])
def Getusert():
	#para receber o token do user (ainda nao funciona)
	content = request.get_json()
	print(content["name"])
	print(content["url"])
	return jsonify( [{"result": "ACK init"}] )

@app.route('/API/User/PostmyLocation', methods=['POST'])
def PostmyLocal():
	#User envia localizaçao e nome e atualiza. Isto depois deve atualizar na BD
	content = request.get_json()
	print(content["name"])
	print(content["location"])
	name = content["name"]
	Location = content["location"]
#	addLog(name,Location)
#	print(logs)
	return jsonify( [{"result": "Logs updated"}] )

@app.route('/API/User/SendBroadMsg', methods=['POST'])
def SendMsg():
	return jsonify( {"aaa":12, "bbb": ["bbb", 12, 12] })

@app.route('/API/User/DefineDistance', methods=['POST'])
def DefineRange():
	return jsonify( {"aaa":12, "bbb": ["bbb", 12, 12] })

@app.route('/API/User/RecvMsg', methods=['GET'])
def RecvMsg():
	return jsonify( {"aaa":12, "bbb": ["bbb", 12, 12] })


# Bots API

# Other Servers API

if __name__ == '__main__':
	app.run()
