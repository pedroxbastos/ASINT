from flask import Flask
from flask import jsonify
from flask import request

	
logs = {}		

def addLog(name,Location):
	logs.update({name:Location})

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/API/Admin/GetBuildsLocations')
def BuildsLocations():
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

@app.route('/API/User/init', methods=['POST'])
def Getusert():
	content = request.get_json()
	print("RRRRRRRRRRRRRRRRREEEEEEEEEEEEEEEEEEEECCCCCCCCCCCEBBBBBBBBBBIIIIIIIIIII")
	print(content["name"])
	print(content["url"])
	return jsonify( [{"result": "ACK init"}] )

@app.route('/API/User/PostmyLocation', methods=['POST'])
def PostmyLocal():
	content = request.get_json()
	print(content["name"])
	print(content["location"])
	name = content["name"]
	Location = content["location"]
	addLog(name,Location)
	print(logs)
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


if __name__ == '__main__':
    app.run()
