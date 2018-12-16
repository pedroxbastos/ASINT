import requests
import getpass
import json
import building
import datetime
from Logs import message_log, move_log

class AdminUI:
    def auth(self):
        count = 0
        print("Administrator application.")
        while count < 3:
            user = input("username: ")
            pwd = getpass.getpass("password: ")
            if user == 'admin' and pwd == '123':
                return True
            else:
                print("Wrong user/pass. %d attempts left." % (2 - count))
                count = count + 1
        return False

    def menu(self):
        exit_ = False
        #client = MongoClient('mongodb://pedroxbastos:Pb9127416716@ds025180.mlab.com:25180/asint')
        #db = client.asint
        while not exit_:
            print("Choose the function to be executed with its name:")
            l = input("\n1-blocal -Insert Building Location\n"
                      "2-ListLogged -List users logged in\n"
                      "3-ListInside -List users inside a building\n"
                      "4-UserHist - History of a user\n"
                      "5-listbuildings - List available buildings\n"
                      "6-AddBot - add a messaging bot\n"
                      "7-quit\n")
            l = l.split()
            if len(l) == 1:
                command = l[0].upper()
                if command == 'QUIT':
                    print("Exiting app by user request.")
                    exit_ = True
                elif command == "INSERT":
                    self.insertLog()
                elif command == 'BLOCAL':
                    self.insertBuildings()
                elif command == 'LISTBUILDINGS':
                    #  Retrieve list of buildings in the database
                    campus = input("Which campus, taguspark, alameda, nuclear or all? ").lower()
                    if campus in ['taguspark', 'alameda', 'nuclear', 'all']:
                        self.getBuildings(campus)
                    else:
                        print("Wrong campus choice. PLease try again.")

                elif command == 'LISTLOGGED':
                    self.listLogged()

                elif command == 'LISTINSIDE':
                    campus = input("which campus?")
                    if campus not in ["taguspark", "alameda", "nuclear"]:
                        print("Wrong campus input.")
                    else:
                        buildingID = input("Which building ID?")
                        self.listInside(buildingID, campus)

                elif command == 'USERHIST':
                    userID = input("What is the userID? ")
                    if userID[:3] != "ist":
                        print("Wrong input")
                    else:
                        self.getHistory(userID)


    def insertBuildings(self):
        #  Select campus
        campus_ = input("Please indicate the campus for the file (Taguspark, Alameda, or Nuclear): ").lower().split()
        if campus_ == "" or (campus_[0] != "taguspark" and campus_[0] != "alameda" and campus_[0] != "nuclear"):
            print("Wrong campus input. Returning to the menu \n\n")
        else:
            #  Request file with buildings in the specified format
            path = input('File (in JSON format) path: ')
            f = open(path, "r")
            data = json.load(f)
            campus = {"campus": campus_[0]}
            spaces = data['containedSpaces']
            f_spaces = []
            f_spaces.append(campus)
            i = 0
            while i < len(spaces):
                b = building.building(data['name'], spaces[i]['id'], spaces[i]['name'], spaces[i]['latitude'],
                                      spaces[i]['longitude'])
                f_spaces.append(b.toDict())
                i = i + 1
            payload = json.dumps(f_spaces)
            r = requests.post("http://127.0.0.1:5000/API/Admin/GetBuildsLocations", json=payload)
            print(r.status_code)
            data = r.json()
            print(data)
            return

    def getBuildings(self, campus):
        payload = {"campus": campus}
        r = requests.post("http://127.0.0.1:5000/API/Admin/GetBuildingList", json=payload)
        data = r.json()
        print(type(data))
        print(data.replace("'","\""))
        new = json.loads(data.replace("'","\""))
        print(type(new))
        for i in new:
            print(i)
        return

    def listInside(self, buildingID, campus):
        payload = {"building_id" : buildingID, "campus" : campus}
        r = requests.post("http://127.0.0.1:5000/API/Admin/GetListAllUsersInBuild", json=payload)
        data = r.json()
        try:
            new = json.loads(data.replace("'", "\""))
            if len(new) == 0:
                print("vazia")
            for i in new:
                print(i)
        except:
            pass
        return

    def getHistory(self, userID):
        payload = {"userID": userID}
        r = requests.post("http://127.0.0.1:5000/API/Admin/GetListHistory", json=payload)
        data = r.json()
        print(type(data))
        print(data.replace("'", "\""))
        try:
            new = json.loads(data.replace("'", "\""))
            print(type(new))
            if len(new) == 0:
                print("vazia")
            for i in new:
                print(i)
        except:
            pass
        return

    def listLogged(self):
        r = requests.post("http://127.0.0.1:5000/API/Admin/")
        print("TODO")
        return

    def insertBot(self):
        print("TODO")
        return

    def insertLog(self):
        type = input("type: ")
        if type == "message":
            to = input("To: ")
            from_ = input("From: ")
            msg = input("msg? ")
            date = str(datetime.datetime.now())
            l = message_log(date, to, from_,msg, "1", "nuclear")
        else:
            userID = input("userID: ")
            date = str(datetime.datetime.now())
            l = move_log(date, "0", userID, "1", "nuclear")

        print(l)
        payload = json.dumps(l.toDict())
        r = requests.post("http://127.0.0.1:5000/API/insert", json=payload)
        print(r.status_code)
        return


