import atexit
import requests
import sys
import threading
import json
# v2.x version - see https://stackoverflow.com/a/38501429/135978
# for the 3.x version
#from apscheduler.scheduler import Scheduler
#from flask import Flask

#app = Flask(__name__)
import sched, time

class Bot:
	def __init__(self):
		print("ola")
		r = requests.get("http://127.0.0.1:5000/API/Bot/init")
		data = r.json()
		for key, value in data.items():
			if key != "error":
				
				self.token=str(data)
				print("my token is: "+ self.token)
				self.start_send()
			else:
				sys.exit(value)

	def start_send(self):
		starttime=time.time()
		while True:
			Message = {"content": "Nao corram dentro do edificio sff"}
			print("Doing stuff...")
			payload = Message
			r = requests.post("http://127.0.0.1:5000/API/Bot/SendBroadMsg/"+self.token, json=payload)
			time.sleep(5.0 - ((time.time() - starttime) % 5.0))


	
if __name__ == '__main__':
    Bot = Bot()

