import atexit

# v2.x version - see https://stackoverflow.com/a/38501429/135978
# for the 3.x version
from apscheduler.scheduler import Scheduler
from flask import Flask

app = Flask(__name__)

cron = Scheduler(daemon=True)
# Explicitly kick off the background thread
cron.start()

Message = {"content": "Nao corram dentro do edificio sff"}
period = 1


@cron.interval_schedule(minute=period)
def job_function():
    payload = Message
    r = requests.post("http://127.0.0.1:5000/API/Bot/SendBroadMsg/Bot1", json=payload)


# Do your work here


# Shutdown your cron thread if the web process is stopped
atexit.register(lambda: cron.shutdown(wait=False))

if __name__ == '__main__':
    app.run(debug=True, port=8000)