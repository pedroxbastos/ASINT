import datetime

class message_log:

    def __init__(self, date, to, from_, message, building_id, campus):
        self.date=date
        self.to=to
        self.from_ = from_
        self.message = message
        self.building_id = building_id
        self.campus = campus
        self.sent = 0


    def __str__(self):
        return "LogType: Message. Date : %s;  From %s to %s in building %s, campus %s. Message: %s" % (self.date, self.from_, self.to, self.building_id, self.campus, self.message)

    def toDict(self):
        return {"date" : self.date, "type" : "message","sent":self.sent, "from" : self.from_, "to" : self.to, "building" : self.building_id, "campus" : self.campus, "message": self.message}

class move_log:

    def __init__(self, checkin, checkout, user, building_id, campus, latitude, longitude):
        self.date = checkin
        self.checkout = checkout
        self.user = user
        self.building_id = building_id
        self.location = {"latitude": latitude, "longitude" : longitude}
        self.campus = campus
        self.range = 30

    def __str__(self):
        return "LogType: Move. User %s - Checkin: %s, Checkout %s; Building %s, Campus %s" % (self.user, self.date, self.checkout, self.building_id, self.campus)

    def toDict(self):
        return {"type" : "move", "user" : self.user, "checkin" : self.date, "checkout" : self.checkout,
                "location": self.location, "building" : self.building_id, "campus" : self.campus}
