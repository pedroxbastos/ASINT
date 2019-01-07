import requests
import getpass
import json
import building
import datetime
from Logs import message_log, move_log
import os.path
from pymongo import MongoClient, errors


class AdminUI:
    def __init__(self):
        self.token_bot_queue = []

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
        db_client = MongoClient('mongodb://pedroxbastos:Pb9127416716@ds025180.mlab.com:25180/asint')
        db = db_client['asint']
        while not exit_:
            try:
                print("\n\nChoose the function to be executed with its name:")
                l = input("\n1-blocal -Insert Building Location\n"
                          "2-ListLogged -List users logged in\n"
                          "3-ListInside -List users inside a building\n"
                          "4-UserHist - History of a user\n"
                          "5-BuildingHist - History on a given buildin\n"
                          "6-listbuildings - List available buildings\n"
                          "7-AddBot - add a messaging bot\n"
                          "8-quit\n"
                          "9-insert - dummy logs insertion\n")
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
                    elif command == "BUILDINGHIST":
                        campus = input("What campus?")
                        if campus not in ["taguspark", "alameda", "nuclear"]:
                            print("Wrong campus input.")
                        else:
                            buildingID = input("What is the building ID?")
                            self.getBHistory(campus,buildingID)
                    elif command == "ADDBOT":
                        campus = input("What campus?")
                        if campus not in ["taguspark", "alameda", "nuclear"]:
                            print("Wrong campus input.")
                        else:
                            L=[]
                            for obj in db[campus].find():
                                print(str(obj["name"]), obj["id"])
                                L.append(obj["id"])
                        buildingID = input("What is the building ID?")
                        if buildingID in L:
                            self.insertBot(campus, buildingID)
                        else:
                            print("No building with the given ID.")
            except KeyboardInterrupt:
                exit_=True


    def insertBuildings(self):
        #  Select campus
        campus_ = input("Please indicate the campus for the file (Taguspark, Alameda, or Nuclear): ").lower().split()
        if campus_ == "" or (campus_[0] != "taguspark" and campus_[0] != "alameda" and campus_[0] != "nuclear"):
            print("Wrong campus input. Returning to the menu \n\n")
        else:
            #  Request file with buildings in the specified format
            path = input('File (in JSON format) path: ')
            try:
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
                r = requests.post("https://asint1-227912.appspot.com/API/Admin/GetBuildsLocations", json=payload)
                data = r.json()
                print(data)
            except IOError:
                print("Error opening the file. Check if it exists or the path is correct.")
            except KeyError as e:
                print(e)
                print("Wrong format for the information in the file.")
            except json.decoder.JSONDecodeError as je:
                print(je)
                print("Error in the json format.")
        return

    def getBuildings(self, campus):
        payload = {"campus": campus}
        r = requests.post("https://asint1-227912.appspot.com/API/Admin/GetBuildingList", json=payload)
        data = r.json()
        new = json.loads(data.replace("'","\""))
        if new == []:
            if campus != "all":
                print("No buildings in %s yet." % campus)
            else:
                print("No building in any campus yet.")
        else:
            for i in new:
                print(str(i))
        return

    def listInside(self, buildingID, campus):
        payload = {"building_id" : buildingID, "campus" : campus}
        r = requests.post("https://asint1-227912.appspot.com/API/Admin/GetListAllUsersInBuild", json=payload)
        data = r.json()
        try:
            new = json.loads(data.replace("'", "\""))
            if len(new) == 0:
                print("vazia")
            for i in new:
                print(str(i))
        except:
            print(data)
        return

    def getHistory(self, userID):
        payload = {"userID": userID}
        r = requests.post("https://asint1-227912.appspot.com/API/Admin/GetListHistory", json=payload)
        data = r.json()
        try:
            new = json.loads(data.replace("'", "\""))
            if len(new) == 0:
                print("vazia")
            for i in new:
                print(str(i))
        except:
            print(data)
        return

    def listLogged(self):
        r = requests.post("https://asint1-227912.appspot.com/API/Admin/GetListAllUsersLogged")
        data = r.json()
        try:
            new = json.loads(data.replace("'", "\""))
            if len(new) == 0:
                print("vazia")
            for i in new:
                print(str(i))
        except:
            print(data)
        return

    def insertBot(self, campus, buildingID):
        r = requests.post("https://asint1-227912.appspot.com/API/Admin/Addbot", json={"addbot": [campus, buildingID]})
        print(r)
        data=r.json()
        print("Insert the following token in the new bot creation: ")
        print(data['token'])
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
        r = requests.post("https://asint1-227912.appspot.com/API/insert", json=payload)
        print(r.status_code)
        return

    def getBHistory(self, campus, BuildingID):
        payload = {"campus": campus, "buildingID": BuildingID }
        r = requests.post("https://asint1-227912.appspot.com/API/Admin/GetListHistory", json=payload)
        data = r.json()
        try:
            new = json.loads(data.replace("'", "\""))
            if len(new) == 0:
                print("vazia")
            for i in new:
                print(str(i))
        except:
            print(data)
        return

if __name__ == '__main__':
    menu = AdminUI()
    menu.menu()