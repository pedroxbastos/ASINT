from flask import Flask,redirect,request
from flask import jsonify
from flask import render_template
import requests
import fenixedu

class user:
	def __init__(self, name):
		self.name=name

app = Flask(__name__)

newuser = user(None)

@app.route('/')
def hello_world():
	return render_template("siteinit.xhtml") 

@app.route('/User/Login')
def login_fenix():
	newuser.name = (str(request.args["LoginId"]))
	print(newuser.name)
	config = fenixedu.FenixEduConfiguration('1977390058176578', 'http://127.0.0.1:5002/User/Mainpage', 'XUwJJfct3cBy7jBbS+NOQVqrQ1eQGN1F9kYAWI3MCMpxgG/J4+h3Qv9+GmOS0Fs+F+Aml8kkZVXroJIb8SZyRw==', 'https://fenix.tecnico.ulisboa.pt/')
	client = fenixedu.FenixEduClient(config)
	url = client.get_authentication_url()
	server = 'http://127.0.0.1:5000/User/init'
	print(url)
	#r = requests.post(server, data={'url': url.split('=')[1]})
	return redirect(url, code=302)

@app.route('/User/Mainpage')
def main_user():
	content = request.get_json()
	print(content)
	return render_template("Usertemplate.xhtml", LoginId = str(newuser.name))


if __name__ == '__main__':
	app.run("127.0.0.1",5002)
