from flask import Flask,redirect,request
from flask import jsonify
from flask import render_template
import requests
import fenixedu
import json

class user:
	def __init__(self, name):
		self.name=name

app = Flask(__name__)

newuser = user(None)
urltrue = None
@app.route('/')
def hello_world():
	return render_template("siteinit.xhtml") 

config = fenixedu.FenixEduConfiguration('1695915081465925', 'http://127.0.0.1:5002/User/Mainpage', 'd/USUpUYU7o20hWNwEi+S3PWW5Cc4ypiQrX3rUfxLAcFat0epdCuxjS35iIWNwJ4ruCu9D7bL2GXZc9P4RDNvQ==', 'https://fenix.tecnico.ulisboa.pt/')
client = fenixedu.FenixEduClient(config)
url = client.get_authentication_url()

@app.route('/User/Login')
def login_fenix():
	newuser.name = (str(request.args["LoginId"]))
	return redirect(url, code=302)
	
@app.route('/User/Mainpage')
def main_user():
	return render_template("Usertemplate.xhtml", LoginId = str(newuser.name))

@app.route('/User/getToken', methods=['POST'])
def getToken():
	content = request.get_json()
	print(str(content))
	print(str(content["code"]))
	print(str(content["code"]).split('=')[1])
	#url = "http://127.0.0.1:5000/API/User/Tokencode"
	user = client.get_user_by_code(str(content["code"]).split('=')[1])
	person = client.get_person(user)
	print(person)
	#r = r.json()
	#print(data)
	#print(user)
	#new = json.loads(jsonify(user))
	#json.dumps(new, indent=4, sort_keys=True)
	#person = client.get_person(user)
	#new2 = json.loads(person)	
	#json.dumps(new2, indent=4, sort_keys=True)
	return jsonify( [{"result": "Logs updated"}] )



if __name__ == '__main__':
	app.run("127.0.0.1",5002)
