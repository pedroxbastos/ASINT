import requests
import sys
import time

class Bot:
	def __init__(self):
		self.interval = int(input("Bot insertion\nDesired time interval in seconds?"))

		self.message = input("Message to be shown?\n")
		self.token = input("Insert the given administrator authorization token\n")

		try:
			r = requests.get("https://asint1-227912.appspot.com/API/Bot/init/"+self.token)
		except requests.exceptions.RequestException as e:
			print("Error trying to reach the server:\n%s\n\n. Please try again and make sure the server is online." % e)
			exit(-1)
		data = r.json()

		if data["response"] == "OK":
			print("Bot authorized! Starting...")
			self.start_send()
		else:
			print("Bot not authorized. Exiting.")
			sys.exit(0)

	def start_send(self):
		while True:
			try:
				payload = {"content": self.message, "token": self.token}
				try:
					r = requests.post("https://asint1-227912.appspot.com/API/Bot/SendBroadMsg", json=payload)
				except requests.exceptions.RequestException as e:
					print("Error trying to reach the server:\n%s\n\n" % e)
				if r.status_code == 200:
					print("Bot message sent!")
				else:
					print("Bot message not sent!")

				if r.json()["response"] == "OK":
					time.sleep(self.interval)
				else:
					print("There was an error. Exiting")
					sys.exit()
			except KeyboardInterrupt:
					print("Bot closing!")
					sys.exit()

if __name__ == '__main__':
    Bot = Bot()

