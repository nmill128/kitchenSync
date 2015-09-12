
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

def getDate():
	return mydate.strtftime("%m%d%Y")

@app.route('/')
def index():
    return "<h1> This flask app is running!<h1>"

@app.route('/Users')
def getUsers():
	record = db.Users.find_one()
	email = record["email"]
	password = record["password"]
	name = record["name"]
	phone = record ["phone"]
	sharing = record["sharing"]
	EXPreminders = record["EXPreminders"]
	friends = record["friends"]
	jsonstr = {"email":email, "password":password, "name":name, "phone":phone, "sharing":sharing, "EXPreminders":EXPreminders, "friends":friends}
	return json.dumps(jsonstr)

@app.route('/CheckIn', methods = ['Post'])
def checkIn():
	nfc = request.form["nfc"]
	userId = request.form["userId"]
	foodRecord = db.stock.find_one({"nfc":nfc})
	name = foodRecord["Brand"]
	upc = foodRecord["upc"]
	category = foodRecord["Category"]
	ExpDate = foodRecord["ExpDate"]
	Amount = foodRecord["Amount"]
	Date_added = Date_updated = getDate()
	db.fridge.insert({"UserId": userId,"nfc":nfc, "upc":upc, "Brand":Brand, "Category":category, "ExpDate":ExpDate, "Date_added":Date_added, "Date_updated":Date_updated})
	#name, expiration date, string "added"
	jsonstr = {"Name":name, "ExpDate":ExpDate, "Status":"Added"}
	return json.dumps(jsonstr)

@app.route('/CheckOut', methods = ['Post'])
def checkOut():
	nfc = request.form["nfc"]
	#temp record
	record = db.stock.find_one({"nfc":nfc})
	# Delete it from the fridge area
	db.fridge.delete_one("nfc":nfc)
	#Add its info to the restock area
	db.restock.insert({"upc":record["upc":upc],"nfc":record["nfc":nfc],"User":record["User":user], "Date_Used":mydate.strtftime("%m%d%Y")})
	return "Success"

@app.route('/Use', methods = ['Post'])
def useOne():
	nfc = request.form["nfc"]
	user = request.form["userId"]
	record = db.stock.find_one({"nfc":nfc})
	amount = record["amount"]
	ssize = record["ssize"]
	newAmount = amount - ssize;
	db.stock.update_one({"nfc":nfc},{"amount":newAmount})
	return 'Success'

@app.route('/login', methods = ['Get'])
def login():
	email = request.form["email"]
	password = request.form["password"]
	record = db.users.find_one({"email":email})
	if(record["password"] == password):
		return json.dumps({"UserId":record["UserId"]})
	elif:
		return "User Authentication Failed"

@app.route('/Stock', methods = ['Get'])
def getStock():
	user = request.form["userId"]


	


if __name__=='__main__':
    app.run(port=8000)
