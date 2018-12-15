class building:

    def __init__(self, campus, id, name, latitude, longitude):
        self.campus = campus
        self.id = id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude


    def __str__(self):
        return "Id: %s - Name: %s - Lat: %s - Lon: %s ;Campus: %s" % (self.id, self.name, self.latitude, self.longitude, self.campus)

    def toDict(self):
        return {"id": self.id, "name": self.name, "latitude": self.latitude, "longitude": self.longitude, "campus": self.campus}