
import flask
import pymongo
import json
import bson.json_util
from flask import Flask
from pymongo import MongoClient


app = Flask(__name__)
app.debug = True
try:
    client=pymongo.MongoClient()
    print "Connected successfully!!!"
except pymongo.errors.ConnectionFailure, e:
   print "Could not connect to MongoDB: %s" % e 
db = client.test

class DateTimeEncoder(json.JSONEncoder):
  def default(self, obj):
      if isinstance(obj, datetime):
          encoded_object = list(obj.timetuple())[0:6]
      else:
          encoded_object =json.JSONEncoder.default(self, obj)
      return encoded_object

@app.route('/')
def index():
    return "<h1> This flask app is running!<h1>"

@app.route('/Users')
def getUsers():
	print "I'm in the function"
	#print db.users
	#client.users.insert({"name":"Yeomans"})
	# return client.users.find_one()
	# print client.database_names()
	# print "Users"
	# print db.users
	# print "Restock"
	# print db.restock.find_one()
	# print "Fridge"
	# print db.fridge
	# print "Stock"
	# print db.stock

	 
	record = db.restock.find_one()
	obj_id = record["Object ID"]
	food_id = record["Food_ID"]
	user = record["User"]
	Date_Used = record[Date_Used]
	jsonstr {"ID": obj_id, "Food_ID":food_id,"User":user, "Date-Used":Date_Used}
	return json.dumps(jsonstr)
# @app.route('/Trial')
# def getTrial():
# 	return "hi"

# @app.route('/Tester')
# def tryTest():
# 	user = users.find_one()
# 	return "hi"

if __name__=='__main__':
    app.run(port=8000)
