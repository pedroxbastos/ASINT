import atexit
import requests
# v2.x version - see https://stackoverflow.com/a/38501429/135978
# for the 3.x version
#from apscheduler.scheduler import Scheduler
#from flask import Flask

#app = Flask(__name__)
import sched, time

Message = {"content": "Nao corram dentro do edificio sff"}
s = sched.scheduler(time.time, time.sleep)
def do_something(sc): 
    print("Doing stuff...")
    payload = Message
    r = requests.post("http://127.0.0.1:5000/API/Bot/SendBroadMsg/Bot1", json=payload)
    # do your stuff
    s.enter(2, 1, do_something, (sc,))

s.enter(2, 1, do_something, (s,))
s.run()

