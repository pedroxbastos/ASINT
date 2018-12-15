from flask import Flask,redirect
from flask import jsonify
from flask import request
import requests
import fenixedu
import pymongo
from pymongo import MongoClient
import pprint
	
Messages = {}		
client = MongoClient('mongodb://pedroxbastos:Pb9127416716@ds025180.mlab.com:25180/asint')
db = client.asint

def addLog(name,location):
	logs.update({"name":name, "localization": location})

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/API/Admin/GetBuildsLocations')
def BuildsLocations():
	#Isto está errado. É suposto o administrador fornecer o ficheiro com os edificios e localizaçoes, o server mete tudo na BD
    return jsonify(str( {"type" : "CAMPUS","id" : "2448131360898","name" : "Taguspark","containedSpaces" : [ {"type" : "BUILDING","id" : "2448131365084","name" : "Edifício principal","topLevelSpace" : {"type" : "CAMPUS","id" : "2448131360898","name" : "Taguspark"}} ]}))

@app.route('/API/Admin/GetListAllUsersLogged', methods=['GET'])
def ListUsersLogged():
    return jsonify( {"aaa":12, "bbb": ["bbb", 12, 12] })

@app.route('/API/Admin/GetListAllUsersInBuild', methods=['GET'])
def ListUsersInsideB():
    return jsonify( {"aaa":12, "bbb": ["bbb", 12, 12] })

@app.route('/API/Admin/GetListHistory', methods=['GET'])
def getUserHistory():
	return jsonify( {"aaa":12, "bbb": ["bbb", 12, 12] })

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

@app.route('/API/User/RecvMsg/<idUser>', methods=['GET'])
def RecvMsg(idUser):
	collection = db.logs
	data = {}
	for key,values in Messages.items():
		if key == idUser:
			data[key] = values
			Messages[key] = []
	return jsonify(data)


if __name__ == '__main__':
    app.run()
