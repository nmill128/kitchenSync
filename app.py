
import flask
import pymongo
import json
import bson.json_util
import os
from twilio.rest import TwilioRestClient
from twilio import twiml
from flask import Flask, g, request, render_template
from pymongo import MongoClient
from datetime import datetime

#Flask setup
app = Flask(__name__,static_url_path='/static')
app.debug = True
try:
    client=pymongo.MongoClient()
    print "Connected successfully!!!"
except pymongo.errors.ConnectionFailure, e:
   print "Could not connect to MongoDB: %s" % e 
db = client.test


#Twilio stuff
account="AC7fe706b555283cfe832a73bc4e276788"
token="d1e515b4d1a316ca7fb4a40ace251d8e"
client = TwilioRestClient(account, token)

#This is how we create a Twilio Message
#Right now they can only go to my phone and Yeomans'
#message = client.sms.messages.create(to=+17038557270, from_=+17038103574,body="Hello there!")



#User Counter
Users = 0


def getDate(dt):
	return dt.strftime("%m%d%y")

@app.route('/')
def index():
	#message = client.sms.messages.create(to=+17038557270, from_=+17038103574,body="Hello there!")
	return "<h1>Hi Ben!<h1>"

@app.route('/<username>/dashboard')
def userDash(username):
	record = db.users.find_one({"username":username})
	print record
	

	return render_template('dashboard.html',stock=db.fridge.find(),restock=db.restock.find())

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
	status = ""
	record = db.fridge.find_one({"nfc":nfc})
	print nfc
	if (not record == None):
		print "Found"
		Date_added = record["Date_added"]
		Date_updated = datetime.now()
		db.fridge.update({"nfc":nfc}, {"UserId": userId,"nfc":nfc, "upc":upc, "Name":name, "Category":category, "amount":Amount, "ExpDate":ExpDate, "Date_added":Date_added, "Date_updated":Date_updated})
		status = "Using"
	else:
		print "New"
		Date_added = Date_updated = datetime.now()
		db.fridge.insert({"UserId": userId,"nfc":nfc, "upc":upc, "Name":name, "Category":category,"amount":Amount, "ExpDate":ExpDate, "Date_added":Date_added, "Date_updated":Date_updated})
		status = "Added"

	#name, expiration date, string "added"
	jsonstr = {"Name":name, "ExpDate":getDate(ExpDate), "Status":status}
	return json.dumps(jsonstr)

@app.route('/Plus', methods = ['POST'])
def addOne():
	nfc = request.form["nfc"]
	print nfc
	userId = request.form["userId"]
	foodRecord = db.food.find_one({"nfc":long(nfc)})
	name = foodRecord["name"]
	upc = foodRecord["upc"]
	category = foodRecord["category"]
	ExpDate = foodRecord["exp"]
	ssize = foodRecord["ssize"]
	record = db.fridge.find_one({"nfc":nfc})
	Amount = record["amount"]+1
	Date_added = record["Date_added"]
	Date_updated=datetime.now()
	status = ""
	print "Adding"
	db.fridge.update({"nfc":nfc},{"UserId": userId,"nfc":nfc, "upc":upc, "Name":name, "Category":category, "amount":Amount, "ExpDate":ExpDate, "Date_added":Date_added, "Date_updated":Date_updated})
	jsonstr = {"Name":name, "Amount":Amount, "ssize":ssize}
	return json.dumps(jsonstr)

@app.route('/Minus', methods = ['POST'])
def subOne():
	nfc = request.form["nfc"]
	print nfc
	userId = request.form["userId"]
	foodRecord = db.food.find_one({"nfc":long(nfc)})
	name = foodRecord["name"]
	upc = foodRecord["upc"]
	category = foodRecord["category"]
	ExpDate = foodRecord["exp"]
	ssize = foodRecord["ssize"]
	record = db.fridge.find_one({"nfc":nfc})
	Amount = record["amount"]-1
	Date_added = record["Date_added"]
	Date_updated=datetime.now()
	status = ""
	print "Subtracting"
	db.fridge.update({"nfc":nfc},{"UserId": userId,"nfc":nfc, "upc":upc, "Name":name, "Category":category, "amount":Amount, "ExpDate":ExpDate, "Date_added":Date_added, "Date_updated":Date_updated})
	jsonstr = {"Name":name, "Amount":Amount, "ssize":ssize}
	return json.dumps(jsonstr)

@app.route('/CheckOut', methods = ['POST'])
def checkOut():
	nfc = request.form["nfc"]
	userId = request.form["userId"]
	print nfc
	print userId
	#temp record
	record = db.fridge.find_one({"nfc":nfc})
	name = record["Name"]
	string = "Success"
	# Delete it from the fridge area
	db.fridge.remove({"nfc":nfc})
	#Add its info to the restock area
	db.restock.insert({"upc":record["upc"],"nfc":record["nfc"],"UserId":record["UserId"], "Date_Used":datetime.now()})
	jsonstr = {"name":name, "string":string}
	return json.dumps(jsonstr)

@app.route('/<username>/delete', methods = ["POST"])
def delete(username):
	print "delete moo"
	nfc = request.form["nfc"]
	print nfc
	# Delete it from the fridge area
	db.fridge.remove({"nfc":nfc})
	record = db.users.find_one({"username":username})
   	return render_template('kitchenTable.html',stock=db.fridge.find())
	
@app.route('/<username>/shareTrue', methods = ['POST'])
def shareTrue(username):
	userId = request.form["userId"]
	record = db.user.find_one({"username":username})
	db.users.insert({"UserId":userId, "username":record["Username"], "password":record["password"], "name":record["name"], "phone":record["phone"], "sharing":True, "EXPreminders":record["EXPreminders"], "friends":record[friends]})


@app.route('/<username>/shareFalse', methods = ['POST'])
def shareFalse(username):
	userId = request.form["userId"]
	record = db.user.find_one({"username":username})
	db.users.insert({"UserId":userId, "username":record["Username"], "password":record["password"], "name":record["name"], "phone":record["phone"], "sharing":False, "EXPreminders":record["EXPreminders"], "friends":record[friends]})

@app.route('/<username>/addFriend', methods = ["POST"])
def addFriend(username):
	friendName = request.form["friend"]
	record = db.user.find_one({"username":username})
	db.users.insert({"UserId":userId, "username":record["Username"], "password":record["password"], "name":record["name"], "phone":record["phone"], "sharing":record["sharing"], "EXPreminders":record["EXPreminders"], "friends":record[friends].append(friendName)})


# @app.route('/<username>/requestFood', methods = ["POST"])
# def requestFood(username):
# 	foodName = request.form["foodName"]
# 	record = db.user.find_one({"username":username})
# 	friends = record["friends"]
# 	for friend in friends:
# 		f = db.user.find_one("username":friend)
# 		number = "1"+f["phone"]
# 		message = client.sms.messages.create(to=+long(number), from_=+17038103574,body="Hello!\n Your friend " + record["name"]+ " needs " + foodName)

@app.route('/twilio/sms', methods = ["POST"])
def response():
	from_number = request.values.get('From', None)
	print from_number
	readableNumber = from_number[2:12]
	print readableNumber
	record = db.users.find_one({"phone":str(readableNumber)})
	userId = record["UserId"]
	foods = db.restock.find({"userId":userId})
	string = "You are out of:\n"
	for f in foods:
		name = f["name"]
		date_used = f["Date_Used"] 
		string.append(name + " Used on: " + date_used +"\n")
	r = twiml.Response()

	r.message("Welcome to twilio!")
	print(str(r))


@app.route('/<username>')
def dashboard(username):
	record = db.users.find_one({"username":username})
	if (not record == None):
		return username
	else:
		return "daron is a nice lady\n" + username



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
