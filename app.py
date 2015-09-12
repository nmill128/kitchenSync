
import flask
import pymongo
import json
import bson.json_util
import os
from flask import Flask, g, request, render_template
from pymongo import MongoClient
from datetime import datetime


app = Flask(__name__)
app.debug = True
try:
    client=pymongo.MongoClient()
    print "Connected successfully!!!"
except pymongo.errors.ConnectionFailure, e:
   print "Could not connect to MongoDB: %s" % e 
db = client.test

Users = 0


def getDate(dt):
	return dt.strftime("%m%d%Y")

@app.route('/')
def index():
    return "<h1>Hi Ben!<h1>"

@app.route('/Users')
def getUsers():
	record = db.Users.find_one()
	username = record["username"]
	password = record["password"]
	name = record["name"]
	phone = record ["phone"]
	sharing = record["sharing"]
	EXPreminders = record["EXPreminders"]
	friends = record["friends"]
	jsonstr = {"username":username, "password":password, "name":name, "phone":phone, "sharing":sharing, "EXPreminders":EXPreminders, "friends":friends}
	return json.dumps(jsonstr)

@app.route('/AddUser', methods = ['POST'])
def addUser():
	username = request.form["username"]
	password = request.form["password"]
	name = request.form["name"]
	phone = request.form["phone"]
	sharing = request.form["sharing"]
	EXPreminders = request.form["EXPreminders"]
	userId = Users
	Users +=1
	db.users.insert({"UserId":userId, "username":username, "password":password, "name":name, "phone":phone, "sharing":sharing, "EXPreminders":EXPreminders, "friends":{}})
	return "Success"

@app.route('/CheckIn', methods = ['POST'])
def checkIn():
	nfc = request.form["nfc"]
	userId = request.form["userId"]
	foodRecord = db.food.find_one({"nfc":long(nfc)})
	name = foodRecord["name"]
	upc = foodRecord["upc"]
	category = foodRecord["category"]
	ExpDate = foodRecord["exp"]
	Amount = foodRecord["amount"]
	Date_added = Date_updated = datetime.now()
	db.fridge.insert({"UserId": userId,"nfc":nfc, "upc":upc, "Name":Brand, "Category":category, "ExpDate":ExpDate, "Date_added":Date_added, "Date_updated":Date_updated})
	#name, expiration date, string "added"
	jsonstr = {"Name":name, "ExpDate":getDate(ExpDate), "Status":"Added"}
	return json.dumps(jsonstr)

@app.route('/CheckOut', methods = ['POST'])
def checkOut():
	nfc = request.form["nfc"]
	#temp record
	record = db.stock.find_one({"nfc":nfc})
	# Delete it from the fridge area
	db.fridge.delete_one({"nfc":nfc})
	#Add its info to the restock area
	db.restock.insert({"upc":record["upc":upc],"nfc":record["nfc":nfc],"User":record["User":user], "Date_Used":mydate.strtftime("%m%d%Y")})
	return "Success"

@app.route('/Use', methods = ['POST'])
def useOne():
	nfc = request.form["nfc"]
	record = db.stock.find_one({"nfc":nfc})
	amount = record["amount"]
	newAmount = amount - 1;
	db.stock.update_one({"nfc":nfc},{"amount":newAmount})
	return 'Success'




@app.route('/<username>')
def dashboard(username):
	record = db.users.find_one({"username":username})
	if (not record == None):
		return username
	else:
		return "daron is a nice lady\n" + username
@app.route('/<username>/AddFriend', methods=['POST'])
def addFriend(username):
	return 'Hi friend'


# @app.route('/login', methods = ['GET'])
# def login():
# 	username = request.form["username"]
# 	password = request.form["password"]
# 	record = db.users.find_one({"username":username})
# 	if(record["password"] == password):
# 		g.user = record["UserId"]
# 		return json.dumps({"UserId":record["UserId"]})
# 	else:
# 		return "User Authentication Failed"


@app.route('/Stock', methods = ['GET'])
def getStock():
	user = request.form["userId"]


	


if __name__=='__main__':
    app.run(port=8000)
