import requests
import getpass
import json
import building

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
            l = input("\n1-blocal(Insert Building Location)\n"
                      "2-ListLogged(List user logged in)\n"
                      "3-ListInside(List users inside a building)\n"
                      "4-UserHist(History of a user)\n"
                      "5-quit?\n"
                      "6-listbuildings\n")
            l = l.split()
            if len(l) == 1:
                command = l[0].upper()
                if command == 'QUIT':
                    print("Exiting app by user request.")
                    exit_ = True
                elif command == 'BLOCAL':
                    self.insertBuildings()
                elif command == 'LISTBUILDINGS':
                    #  Retrieve list of buildings in the database
                    campus = input("Which campus, taguspark, alameda, nuclear or all? ").lower()
                    if campus in ['taguspark', 'alameda', 'nuclear', 'all']:
                        self.getBuildings(campus)
                    else:
                        print("Wrong campus choice. PLease try again.")

                # elif command == 'LISTLOGGED':
                #     #Está a fazer a ligaçao direta à BD, mas depois deve ser feito admin-server-bd-server-admin
                #     collection = db.logs
                #     for obj in collection.find():
                #         pprint.pprint(obj)
                elif command == 'LISTINSIDE':
                    campus = input("which campus?")
                    if campus not in ["taguspark", "alameda", "nuclear"]:
                        print("Wrong campus input.")
                    else:
                        buildingID = input("Which building ID?")
                        self.listInside(buildingID, campus)

                # elif command == 'USERHIST':
                #     #Ainda não é o comando correto
                #     url = 'http://127.0.0.1:5000/API/Admin/GetListHistory'
                #     r = requests.get(url)
                #     print(r.status_code)
                #     data = r.json()
                #     print(data)

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

    def getHistory(self, userID):
        print(userID)
        return

    def listLogged(selfs):
        print("TODO")
        return


