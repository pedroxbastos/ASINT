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
import secrets


Messages = {}
UsersOn = []

#Bots Online
BotsOn = {}
#Available tokens to init bots
token_bot_queue = []


app = Flask(__name__)
app.secret_key = os.urandom(32)
db_client = MongoClient('mongodb://pedroxbastos:Pb9127416716@ds025180.mlab.com:25180/asint')
db = db_client['asint']


@app.errorhandler(404)
def page_not_found(error):
	flash("You were returned to the initial page due to an error:"
		  " 404 - Page Not Found")
	return render_template("siteinit.xhtml")

@app.errorhandler(400)
def bad_request(error):
	flash("You were returned to the initial page due to an error:"
		  " 400 - Bad Request")
	return render_template("siteinit.xhtml")

@app.errorhandler(500)
def res_not_found(error):
	flash("You were returned to the initial page due to an error:"
		  " 500 - Resource Not Found")
	return render_template("siteinit.xhtml")

@app.after_request
def after_request(response):
	#response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
	return response

@app.route('/')
def hello_world():
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
	x=0
	while session['username'] != UsersOn[i]['username']:
		i +=1
	if UsersOn[i]['count']==1:
		#Caso logout normal.
		UsersOn.pop(i)
		collection = db['logs']
		collection.update_one({"type": "move", "checkout": "0", "user": session['username']}, {"$set":
								{"checkout": str(datetime.datetime.now())}})
	else:
		x = 1
		UsersOn[i]['count'] -=1

	session.pop('logged_in', None)
	session.pop('name', None)
	session.pop('username', None)
	session.clear()
	if x==0:
		flash("You have been logged out!")
	else:
		flash("You have been logged out from this device"
			  " because you entered the application on a different"
			  " device.")
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

	print("Vou fazer print dos userson")
	print(UsersOn)

	user_ = client.get_user_by_code(code)
	person = client.get_person(user_)
	displayName = person['displayName']
	username = person['username']

	i= find_index(UsersOn, 'username', username)
	if i == -1:
		UsersOn.append({"username" : username, "name": displayName, "user":user_, "range":30, "a_token": user_.access_token, "count":1,
						"building":None, "campus": None, "location":None})
		Messages[username] = []
	else:
		# Primeiro fazer o checkout da sessão que estava activa
		collection = db['logs']
		collection.update_one({"type": "move", "checkout": "0", "user": username}, {"$set":
							   {"checkout": str(datetime.datetime.now())}})
		# Atualizar o user no UsersOn
		UsersOn[i]['user'] = user_
		UsersOn[i]['a_token'] = user_.access_token
		UsersOn[i]['count'] +=1

	session['code'] = code
	session['username'] = username
	session['name'] = displayName
	session['logged_in'] = True
	session['a_token'] = user_.access_token
	print("Novo usersON:")
	print(UsersOn)

	return redirect(url_for('MainpageDone'))

@app.route('/User/MainpageDone', methods=['GET'])
@login_required
def MainpageDone():
	return render_template("Usertemplate.xhtml")

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
		#  Ver UsersOn e perguntar aos outros servidores por users em sessions também.
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
				# print(type(ret))
			if len(ret) == 0:
				return json.dumps("There are no users currently in the given building.")
			else:
				return json.dumps(str(ret))


@app.route('/API/Admin/GetListHistory', methods=['POST'])
def getUserHistory():
	if request.method == "POST":
		content = request.json
		if content.__len__() == 1:
			#User history.
			userID = content['userID']
			collection = db["logs"]
			if collection.count_documents({"userID" : userID}) == 0:
				return json.dumps("The are no logs for user %s." % userID)
			else:
				ret = []
				for c in collection.find({"$or":[ {"user":userID}, {"to":userID}, {"from_":userID}]}, {'_id':False}).sort('date',1):
					ret.append(c)
				return json.dumps(str(ret))
		elif content.__len__() == 2:
			#Buiding history
			campus = content["campus"]
			buildingID = content["buildingID"]
			collection = db["logs"]
			if collection.count_documents({"building": buildingID}) == 0:
				return json.dumps("The are no logs for the building with ID %s in campus %s ." % (buildingID, campus))
			else:
				ret = []
				for c in collection.find({"building": buildingID},{'_id':False}).sort('date',1):
					ret.append(c)
				return json.dumps(str(ret))

@app.route('/API/insert', methods=['POST'])
def addLog():
	#  Just for testing.
	content=request.json
	content2 = json.loads(content.replace("'", "\""))
	collection = db["logs"]
	c = collection.insert_one(content2)
	return json.dumps("ok")

@app.route('/API/Admin/Addbot', methods=['GET'])
def addBot():
	content=request.json
	token = secrets.token_urlsafe(16)
	#mensagem do admin {"addbot": ["campus","buildingID"]}
	token_bot_queue.append(token)
	BotsOn[token]=content["addbot"]
	return jsonify({"token":token})


#  User API


@app.route('/API/User/PostmyLocation', methods=['POST'])
def PostmyLocal():

	if getToken(session['username']) != session['a_token']:
		session['logged_in'] = False
		return jsonify({"result": "-1"})

	content = request.json
	i = find_index(UsersOn, 'username', session['username'])
	#  Most recent location inserted into UsersOn
	UsersOn[i]['location']=[content["location"][0], content["location"][1]]
	print(type(UsersOn[i]['location']))
	print(UsersOn[i]['location'])
	print(UsersOn[i]['location'][0])
	print(UsersOn[i]['location'][1])


	building, campus, building_id = getBuilding(content["location"][0], content["location"][1])
	collection = db["logs"]

	if building is None:
		#  No building exists for this coordinates. Verify if there was a change in building aswell
		if collection.count_documents({"type":"move", "checkout":"0", "user": session['username']}) != 0:
			collection.update_one({"type": "move", "checkout": "0", "user": session['username']}, {"$set":
				{"checkout": str(datetime.datetime.now())}})
		UsersOn[i]["building"] = None
		UsersOn[i]["campus"] = None
		return jsonify({"result": "Log not inserted - There's no building in this coordinates", "range":UsersOn[i]['range']})
	else:
		if collection.count_documents({"type":"move", "checkout":"0", "user": session['username']}) == 0:
			#  New log insertion
			collection.insert_one(
				move_log(str(datetime.datetime.now()), "0", session['username'], building_id, campus,
						 content["location"][0], content["location"][1]).toDict())
			UsersOn[i]["building"] = building_id
			UsersOn[i]["campus"] = campus
			return jsonify({"result": "New log was inserted for this location (checkin)", "range":UsersOn[i]['range']})
		else:
			#  Checkin already done, so update the document if the location changed. else do nothing.
			c = collection.find_one({"type":"move", "checkout":"0", "user": session['username']})
			if c['building'] != building_id:
				#  Building change. Checkout of old building and checkin on the new one.
				collection.update_one({"type":"move", "checkout":"0", "user": session['username']},{"$set":
				{"checkout":str(datetime.datetime.now())}})
				collection.insert_one(
					move_log(str(datetime.datetime.now()), "0", session['username'], building_id, campus,
							 content["location"][0], content["location"][1]).toDict())
				# Actualizar building e campus. Location actualizada logo no início.
				UsersOn[i]["building"] = building_id
				UsersOn[i]["campus"] = campus
				return jsonify({"result": "Location was updated", "range":UsersOn[i]['range']})
			else:
				#  Same building, update location only in UsersOn
				#collection.update_one({"type": "move", "checkout": "0", "user": session['username']},
				#					  {"$set": {"location":{"latitude": content["location"][0], "longitude" : content["location"][1]}}})
				#i = find_index(UsersOn, 'username', session['username'])
				#UsersOn[i]["location"] = [content["location"][0], content["location"][1]]
				return jsonify({"result": "Same Location", "range":UsersOn[i]['range']})

@app.route('/API/User/SendBroadMsg/<idName>', methods=['POST'])
def SendMsg(idName):
	collection = db.logs
	content = request.get_json()
	objself=None
	for obj in UsersOn:
		if obj["username"]==session['username']:
			objself=obj
	print(UsersOn)
	for obj in UsersOn:
		if obj != objself:
			if calculateDistance(obj['Location'][0], obj['Location'][1], objself['location'][0], objself['location'][1]) < objself['range']:
				Messages[session["username"]].append(content["Message"])

	print(Messages)
	obj = {"type": "Message", "user": session["username"], "date": datetime.datetime.now(), "content":content["Message"]}
	collection.insert_one(obj)
	return jsonify( {"aaa":12, "bbb": ["bbb", 12, 12] })

@app.route('/API/User/DefineRange', methods=['POST'])
def DefineRange():
	content = request.get_json()
	collection = db["logs"]
	collection.update_one({"type" : "move", "user": session['username'], "checkout":"0"},
						  {"$set":{"range":content['Range']}})
	i=find_index(UsersOn,'username', session['username'])
	UsersOn[i]['range']=float(content['Range'])
	string = "Range updated to %s" % content['Range']
	in_range = []
	in_range = get_users_in_range(session['username'])
	return jsonify({"result":string, "range":UsersOn[i]['range'], "in_range": in_range})


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
@app.route('/API/Bot/init', methods=['GET'])
def get_bot_token():
	print(token_bot_queue)
	if len(token_bot_queue)==0:
		print("erro")
		return jsonify({"error": "no tokens available"})
	else:
		return jsonify({"token": token_bot_queue.pop(0)})


@app.route('/API/Bot/SendBroadMsg/<idBot>', methods=['POST'])
def BotMsgHandle(idBot):
	collection = db.logs
	content = request.get_json()
	for obj in UsersOn:
		#print(value)
		#if value['Building'] == str(idBot):
		print(Messages)
		#if obj["campus"]==BotsOn[token][0] and obj["building"]==BotsOn[token][1]:
		Messages[obj["username"]].append(content["content"])
	return jsonify({"Result": "OK"})

# Other Servers API
# Vai ser preciso para quando uns users estão logged num server e outros noutros e é preciso procurar todos.

#Outros

@app.route('/GetBuilding/<lat>/<long>')
def getBuilding(lat, long):
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
	building_id=""
	in_range=[]
	in_building=[]
	for c in collection.find():
		d = calculateDistance(float(c['latitude']), float(c['longitude']), lat, long)
		if d < min_range:
			min_range = d
			building = c['name']
			building_id = c['id']
	in_range = get_users_in_range(session['username'])
	if min_range == 30.01:
		if request.method == "GET":
			return jsonify({"building" : None, "campus": None, "building_id": None, "in_range":in_range, "in_build":in_building})
		else:
			return None, None, None
	else:
		if request.method == "GET":
			in_building = get_users_in_building(session['username'],building_id)
			return jsonify({"building":building, "campus":campus, "building_id":building_id,"in_build":in_building, "in_range":in_range})
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


def getToken(userID):
	i=0
	while i < len(UsersOn):
		if UsersOn[i]['username'] == userID:
			return UsersOn[i]['user'].access_token
		i +=1
	return 0

def find_index(dicts, key, value):
    class Null: pass
    for i, d in enumerate(dicts):
        if d.get(key, Null) == value:
            return i
    else:
        return -1

def get_users_in_building(userid, buildingid):
	l=[]
	for i in UsersOn:
		if i['username'] != userid and i['building'] == buildingid:
			l.append(i['username'])
	if l.__len__()==0:
		l = None
	print("vou devolver:")
	print(l)
	return l

def get_users_in_range(userid):
	l=[]
	i=find_index(UsersOn, 'username', userid)
	for u in UsersOn:
		if u['location'] is None:
			print("location do %s é None" % u['username'])
		elif u['username'] != userid and UsersOn[i]['range'] > calculateDistance(UsersOn[i]['location'][0],UsersOn[i]['location'][1], u['location'][0], u['location'][1]):
			l.append(u['username'])
	if l.__len__()==0:
		l=None
	print("RANGE:vou devolver:")
	print(l)
	return l

@app.before_first_request
def verify_wrong_logs():
	collection = db['logs']
	z=0
	print("ola!")
	for c in collection.find({"type":"move", "checkout":"0"}):
		checkout = datetime.datetime.strptime(c["checkin"],'%Y-%m-%d %H:%M:%S.%f') + datetime.timedelta(minutes=1)
		collection.update_one({"_id":c["_id"]},{"$set":{"checkout": str(checkout)}})
		z += 1
	print("c é %d"%z)
	return


if __name__ == '__main__':
	app.run()
