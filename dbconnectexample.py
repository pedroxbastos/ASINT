import pymongo                                                                                                   
from pymongo import MongoClient
import pprint                                                                                    
client = MongoClient('mongodb://pedroxbastos:Pb9127416716@ds025180.mlab.com:25180/asint')                           
db = client['asint']                                                                                                
collection = db['buildings']                                                                                        
building = { "type" : "CAMPUS" }
post_id = collection.insert_one(building).inserted_id
post = {  "type" : "CAMPUS",  "id" : "2448131360897",  "name" : "Alameda",  "containedSpaces" : [ {    "type" : "BUILDING",    "id" : "2448131361069",    "name" : "Pavilhão de Acção Social",    "topLevelSpace" : {      "type" : "CAMPUS",      "id" : "2448131360897",      "name" : "Alameda"    }  }, {    "type" : "BUILDING",    "id" : "2448131361173",    "name" : "Pavilhão de Informática II",    "topLevelSpace" : {      "type" : "CAMPUS",      "id" : "2448131360897",      "name" : "Alameda"    }  }, ]}
for obj in db.collection.find():
    pprint.pprint(obj)