from flask import Flask, url_for
from flask import jsonify, redirect
from flask import request, render_template
from flask import session, flash, abort
from pymongo import MongoClient, errors
import pprint
import json
import fenixedu
from fenixedu import user
import requests
from math import radians, cos, sin, asin, sqrt
import datetime
from functools import wraps
import os
from Logs import move_log, message_log


Messages = {}
UsersOn = []
onID = 0
#session.clear()
#logs = {}

#def addLog(name,Location):
#	logs.update({name:Location})

app = Flask(__name__)
app.secret_key = os.urandom(32)
db_client = MongoClient('mongodb://pedroxbastos:Pb9127416716@ds025180.mlab.com:25180/asint')
db = db_client['asint']


@app.errorhandler(404)
def page_not_found(error):
	return "Resource not found", 404

@app.errorhandler(400)
def bad_request(error):
	return("Bad!", 400)

@app.errorhandler(500)
def res_not_found(error):
	return "Resource not found 500", 500

@app.after_request
def after_request(response):
	#response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
	return response


@app.route('/')
def hello_world():
	if session:
		print("ha sessão.")
		print(session['username'])
		print(session['name'])
		print(session['logged_in'])
		print(UsersOn)
	else:
		print("no session")
		print(UsersOn)
	return render_template("siteinit.xhtml") 

def login_required(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash("No logged in user yet.")
			return render_template("siteinit.xhtml")
	return wrap

@app.route('/User/Login')
def login_fenix():
	#  Fenix
	config = fenixedu.FenixEduConfiguration.fromConfigFile('fenixedu.ini')
	client = fenixedu.FenixEduClient(config)
	url = client.get_authentication_url()
	return redirect(url, code=302)

@app.route("/User/Logout", methods = ["POST"])
@login_required
def logout():
	i=0
	print(UsersOn)
	print(session)
	UsersOn.pop(i)
	print(UsersOn)
	collection = db['logs']
	collection.update_one({"type": "move", "checkout": "0", "user": session['username']}, {"$set":
			{"checkout": str(datetime.datetime.now())}})
	session.pop('logged_in', None)
	session.pop('name', None)
	session.pop('username', None)
	session.clear()
	print(session)

	print("Logout Done")
	return redirect(url_for('hello_world'))


@app.route('/User/Mainpage', methods = ['POST', 'GET'])
def main_user():
	#  Needed again
	config = fenixedu.FenixEduConfiguration.fromConfigFile('fenixedu.ini')
	client = fenixedu.FenixEduClient(config)
	try:
		code = request.args['code']
	except KeyError:
		abort(400)

	user_ = client.get_user_by_code(code)
	person = client.get_person(user_)
	displayName = person['displayName']
	username = person['username']
	UsersOn.append({"username" : username, "name": displayName, "user":user_})
	print(username)
	print(displayName)
	session['code'] = code
	session['username'] = username
	session['name'] = displayName
	session['logged_in'] = True
	print(user_.access_token)
	print(user_.refresh_token)
	print(user_.token_expires)

	# UsersOn[onID-1]['access_token']=access_token
	# UsersOn[onID-1]['refresh_token']=refresh_token
	# UsersOn[onID-1]['Location']=None
	# UsersOn[onID-1]['Building']=None
	# UsersOn[onID-1]['Campus']=None
	# UsersOn[onID-1]['Range']=100 #default
	# Messages[UsersOn[onID-1]['name']] = []
	return redirect(url_for('MainpageDone'))

@app.route('/User/MainpageDone', methods=['GET'])
@login_required
def MainpageDone():
	return render_template("Usertemplate.xhtml")

@app.route('/User/getToken', methods=['POST'])
def getToken():
	test = request.json
	#print(test['code'])
	#print("endtest")
	#content = request.get_json()
	#print(str(content))
	#print(str(content["code"]))
	#print(str(content["code"]).split('=')[1])
	#url = "http://127.0.0.1:5000/API/User/Tokencode"
	#user = client.get_user_by_code(str(content["code"]).split('=')[1])
	#person = client.get_person(user)
	#print(person)
	#r = r.json()
	#print(data)
	#print(user)
	#new = json.loads(jsonify(user))
	#json.dumps(new, indent=4, sort_keys=True)
	#person = client.get_person(user)
	#new2 = json.loads(person)	
	#json.dumps(new2, indent=4, sort_keys=True)
	return jsonify( [{"result": "Logs updated"}] )



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
		if content['campus'] not in ["all"]:
			collection = db[content['campus']]
			ret = []
			for c in collection.find({},{'_id': False}):
				ret.append(c)
		else:
			ret=[]
			for cp in ["alameda", "taguspark", "nuclear"]:
				collection = db[cp]
				for c in collection.find({},{'_id':False}):
					ret.append(c)
		return json.dumps(str(ret))

@app.route('/API/Admin/GetListAllUsersLogged', methods=['POST'])
def ListUsersLogged():
		#  Ver sessions e perguntar aos outros servidores por users em sessions também.
	return json.dumps(str(UsersOn))


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



@app.route('/API/User/PostmyLocation', methods=['POST'])
def PostmyLocal():
	#User envia localizaçao e nome e atualiza. Isto depois deve atualizar na BD
	content = request.json
	building, campus, building_id = getBuilding(content["location"][0], content["location"][1])
	print(building)
	print(campus)
	print(building_id)
	if building is None:
		#  No buildin exists for this coordinates
		return jsonify( [{"result": "Log not inserted - There's no building in this coordinates"}] )
	else:
		collection = db["logs"]
		if collection.count_documents({"type":"move", "checkout":"0", "user": session['username']}) == 0:
			#  New log insertion
			collection.insert_one(
				move_log(str(datetime.datetime.now()), "0", session['username'], building_id, campus,
						 content["location"][0], content["location"][1]).toDict())
			return jsonify([{"result": "New log was inserted for this location (checkin)"}])
		else:
			#  Checkin already done, so update the document if the location changed. else do nothing.
			c = collection.find_one({"type":"move", "checkout":"0", "user": session['username']})
			print(c)
			if c['building'] != building_id:
				#  Building change. Checkout of old building and checking on the new one.
				collection.update_one({"type":"move", "checkout":"0", "user": session['username']},{"$set":
				{"checkout":str(datetime.datetime.now())}})
				collection.insert_one(
					move_log(str(datetime.datetime.now()), "0", session['username'], building_id, campus,
							 content["location"][0], content["location"][1]).toDict())
				return jsonify([{"result": "Location was updated"}])
			else:
				#  Same building, update location only
				collection.update_one({"type": "move", "checkout": "0", "user": session['username']},
									  {"$set": {"location":{"latitude": content["location"][0], "longitude" : content["location"][1]}}})
				return jsonify([{"result": "Same Location"}])


	# if getBuilding(content["location"][0], content["location"][1]) == {}
	# 	#  Building não existe na BD.
	# 	return jsonify([{"result": "The given coordinates do not correspond to a stored building"}])
	# if collection.count_documents({"type":"move", })
	#test = session['username'] + "lat -> " + str(content["location"][0]) + "long ->" + str(content["location"][0])
	#print(test)

	# print(content)
	# print(content["name"])
	# location=[content["location"][0], content["location"][1]]
	# building,campus = getBuilding(int(content["location"][0]), int(content["location"][1]))
	# obj = {"type": "move", "user": content["name"], "date": datetime.datetime.now()}
	# for i, value in UsersOn.items():
	# 	if value['naforme']==str(content["name"]):
	# 		if value['Location'] != location:
	# 			value['Location']=[content["location"][0],content["location"][1]]
	# 			value['Building'],value['Campus']=building,campus
	# 			print(value['Building'], value['Campus'])
	# 			obj['Location']=value['Location']
	# 			obj['Building']=value['Building']
	# 			obj['Campus']=value['Campus']
	# 			collection.insert_one(obj)
	# 			return jsonify( [{"result": "Logs updated"}] )
	#return jsonify( [{"result": "Same Location"}] )

@app.route('/API/User/SendBroadMsg/<idName>', methods=['POST'])
def SendMsg(idName):
	collection = db.logs
	content = request.get_json()
	objself=None
	for key,value in UsersOn.items():
		if idName == value['name']:
			objself=key
			print(objself)
		break
	for obj, value in UsersOn.items():
		if obj != objself:
			print(value)
			if calculateDistance(value['Location'][0], value['Location'][1], UsersOn[objself]['Location'][0], UsersOn[objself]['Location'][1]) < UsersOn[objself]['Range']:
				Messages[value['name']].append(content["Message"])

	print(Messages)
	obj = {"type": "Message", "user": UsersOn[objself]['name'], "date": datetime.datetime.now(), "content":content["Message"]}
	collection.insert_one(obj)
	return jsonify( {"aaa":12, "bbb": ["bbb", 12, 12] })

@app.route('/API/User/DefineRange/<idName>', methods=['POST'])
def DefineRange(idName):
	content = request.get_json()
	print(session['username'])
	print(content['Range'])
	collection = db["logs"]
	collection.update_one({"type" : "move", "user": session['username'], "checkout":"0"},
						  {"range":content['Range']})
	return jsonify({"ok":"ok"})
	# for key,value in UsersOn.items():
	# 	if idName == value['name']:
	# 		objself=key
	# 		print(objself)
	# 	break
	# UsersOn[objself]['Range']=int(content["Range"])
	# print("range:"+str(UsersOn[objself]['Range']))
	# return jsonify( {"Result":"Range updated" })

@app.route('/API/User/RecvMsg/<idUser>', methods=['GET'])
def RecvMsg(idUser):
	collection = db.logs
	data = {}
	for key,values in Messages.items():
		if key == idUser:
			data[key] = values
			Messages[key] = []
	return jsonify(data)


# Bots API


@app.route('/API/Bot/SendBroadMsg/<idBot>', methods=['POST'])
def BotMsgHandle(idBot):
	collection = db.logs
	content = request.get_json()
	for obj, value in UsersOn.items():
		print(value)
		if value['Building'] == str(idBot):
			Messages[value['name']].append(content["Message"])
	return jsonify(data)


# Other Servers API
# Vai ser preciso para quando uns users estão logged num server e outros noutros e é preciso procurar todos.

#Outros

@app.route('/GetBuilding/<lat>/<long>')
def getBuilding(lat, long):
	print(request.method)
	if type(lat) != float:
		lat = float(lat)
	if type(long) != float:
		long = float(long)

	#  Given the user's coordinates, returns the building where the user is
	if lat >38.8:
		campus="nuclear"
	elif long < -9.2:
		campus="taguspark"
	else:
		campus="alameda"
	collection = db[campus]
	min_range = 30.01
	building = ""
	for c in collection.find():
		d = calculateDistance(float(c['latitude']), float(c['longitude']), lat, long)
		print("b : %s, d= %f -- min range: %f" % (c['name'], d, min_range))
		if d < min_range:
			min_range = d
			building = c['name']
			building_id = c['id']
	if min_range == 30.01:
		if request.method == "GET":
			return jsonify({"building" : None, "campus": None})
		else:
			return None, None, None
	else:
		if request.method == "GET":
			return jsonify({"building":building, "campus":campus})
		else:
			return building, campus, building_id

def calculateDistance(b_lat, b_long, u_lat, u_long):
	#  haversine formula. Returns the distance between 2 coordinate points in meters
	b_lat, b_long, u_lat, u_long = map(radians, [b_lat, b_long, u_lat, u_long])
	dlon = b_long - u_long
	dlat = b_lat - u_lat
	a = sin(dlat / 2) ** 2 + cos(b_lat) * cos(u_lat) * sin(dlon / 2) ** 2
	c = 2 * asin(sqrt(a))
	r = 6371 * 1000  # Radius of earth in meters.
	return c*r

if __name__ == '__main__':
	app.run()
