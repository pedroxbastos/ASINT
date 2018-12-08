#!/usr/bin/env python
from flask import Flask
import requests
from flask import jsonify
import pymongo                                                                                                   
from pymongo import MongoClient
import pprint

class AdminUI:
    def menu():
        exit = False
        client = MongoClient('mongodb://pedroxbastos:Pb9127416716@ds025180.mlab.com:25180/asint')
        db = client.asint
        while not exit:
            l = input("\n1-blocal(Building Location)\n2-ListLogged(List user logged in)\n3-ListInside(List users inside a building)\n4-UserHist(History of a user)\n5-quit?\n")
            l = l.split()

            if len(l) == 1:
                command = l[0].upper()
                if command == 'QUIT':
                    exit = True
                elif command == 'BLOCAL':
                    url = 'http://127.0.0.1:5000/API/Admin/GetBuildsLocations'
                    r = requests.get(url)
                    print(r.status_code)
                    data = r.json()
                    print(data)
                elif command == 'LISTLOGGED':
                    collection = db.logs
                    for obj in collection.find():
                        pprint.pprint(obj)
                elif command == 'LISTINSIDE':
                    print("Which building?")
                    collection = db.buildings
                    for obj in collection.find({},{ "name": 1, "containedSpaces":1, "containedSpaces.name":1, "_id": 0 }):
                        pprint.pprint(obj)
                    build = input()
                    collection = db.logs
                    for obj in collection.find({"localization": "Alameda"}):
                        pprint.pprint(obj)
                elif command == 'USERHIST':
                    url = 'http://127.0.0.1:5000/API/Admin/GetListHistory'
                    r = requests.get(url)
                    print(r.status_code)
                    data = r.json()
                    print(data)


if __name__ == "__main__":
    AdminUI.menu()
