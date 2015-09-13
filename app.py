
import flask
import pymongo
import json
import bson.json_util
import os
import urllib2
import schedule
import time
from twilio.rest import TwilioRestClient
from twilio import twiml
from flask import Flask, g, request, render_template, redirect
from pymongo import MongoClient
from datetime import datetime,date



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
	return redirect("/KenBapp/dashboard", code=302)

@app.route('/<username>/dashboard')
def userDash(username):
	record = db.users.find_one({"username":username})

	print record
	

	return render_template('dashboard.html',stock=db.fridge.find({"UserId":record["UserId"]}),restock=db.restock.find({"UserId":record["UserId"]}),username=username)

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


@app.route('/exp')
def remindDates():
	records = db.fridge.find()
	string=""
	for r in records:
		string=""
		if (r["ExpDate"].day == date.today().day):
			
			print r["UserId"]
			user = db.users.find_one({"UserId":int(r["UserId"])})
			if (not user == None) and user["EXPreminders"]:
				number = "1"+user["Phone"]
				string = "Your "+ r["Name"] + " expires today."
				message = client.sms.messages.create(to=+long(number), from_=+17038103574,body=string)	
	return(str(string+"Success"))


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
	listRec = db.restock.find_one({"upc":upc})
	if (not listRec==None):
		db.restock.remove({"upc":upc, "UserId":userId})
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
	url = "http://api.walmartlabs.com/v1/items?apiKey=jgz3vtvr9cuwguzrzpn54nuy&upc=" + record["upc"]
	contents=urllib2.urlopen(url).read()
	data = json.loads(contents)
	data = data["items"][0]
	price = "N/A"
	if "msrp" in data:
		price = data["msrp"]
	elif "saleprice" in data:
		price = data["salePrice"]
	db.restock.insert({"name":data["name"],"price":price,"upc":record["upc"],"nfc":record["nfc"],"UserId":record["UserId"], "Date_Used":datetime.now()})
	jsonstr = {"name":name, "string":string}
	return json.dumps(jsonstr)

@app.route('/<username>/delete', methods = ["POST"])
def delete(username):
	nfc = request.form["nfc"]
	# Delete it from the fridge area
	db.fridge.remove({"nfc":nfc})
	record = db.users.find_one({"username":username})
	print record["UserId"]
   	return render_template('kitchenTable.html',stock=db.fridge.find({"UserId":('{0:.3g}'.format(record["UserId"]))}))

@app.route('/<username>/restockDelete', methods = ["POST"])
def restockDelete(username):
	nfc = request.form["nfc"]
	# Delete it from the fridge area
	print nfc
	db.restock.remove({"nfc":nfc})
	record = db.users.find_one({"username":username})
   	return render_template('restockTable.html',restock=db.restock.find({"UserId":('{0:.3g}'.format(record["UserId"]))}))
	
@app.route('/<username>/shareTrue', methods = ['POST'])
def shareTrue(username):
	userId = request.form["userId"]
	record = db.users.find_one({"username":username})
	db.users.insert({"UserId":userId, "username":record["Username"], "password":record["password"], "name":record["name"], "phone":record["phone"], "sharing":True, "EXPreminders":record["EXPreminders"], "friends":record[friends]})


@app.route('/<username>/shareFalse', methods = ['POST'])
def shareFalse(username):
	userId = request.form["userId"]
	record = db.users.find_one({"username":username})
	db.users.insert({"UserId":userId, "username":record["Username"], "password":record["password"], "name":record["name"], "phone":record["phone"], "sharing":False, "EXPreminders":record["EXPreminders"], "friends":record[friends]})

@app.route('/<username>/addFriend', methods = ["POST"])
def addFriend(username):
	friendName = request.form["friend"]
	record = db.users.find_one({"username":username})
	fris = []
	if not record["Friends"] == None:
		for fri in record["Friends"]:
			fris.append(fri)
	fris.append(friendName)
	db.users.update({"UserId":record["UserId"]},{"UserId":record["UserId"], "username":record["username"], "Password":record["Password"], "Name":record["Name"], "Phone":record["Phone"], "Sharing":record["Sharing"], "EXPreminders":record["EXPreminders"], "Friends":fris})
	return "Success"

@app.route('/<username>/requestFood', methods = ["POST"])
def requestFood(username):
	nfc = request.form["nfc"]
	print nfc
	foodRecord = db.food.find_one({"nfc":long(nfc)})
	name = foodRecord["name"]
	print name 
	record = db.users.find_one({"username":username})
	friends = record["Friends"]
	print friends
	for friend in friends:
		print friend
		f = db.users.find_one({"username":friend})
		UserId = f["UserId"]
		rec = db.fridge.find_one({"UserId":UserId, "nfc":long(nfc)})
		if not rec==None:
			number = "1"+f["Phone"]
			message = client.sms.messages.create(to=+long(number), from_=+17038103574,body="Hello!\n Your friend " + record["Name"]+ " needs " + name)
		else:
			return "None of your friends have " + name+"."
	return "Request Sent"

@app.route('/twilio/sms', methods = ["POST"])
def response():
	from_number = request.values.get('From', None)
	print from_number
	readableNumber = from_number[2:12]
	record = db.users.find_one({"Phone":str(readableNumber)})
	userId = record["UserId"]
	foods = db.restock.find({"UserId":str(int(userId))})
	count = foods.count() -1
	counter = 0
	print count
	string = "You are out of:\n"
	while counter <= count:
		f = db.restock.find_one({"UserId":str(int(userId))},skip=counter)
		counter +=1
		print counter
		nfc = f["nfc"]
		print nfc
		r = db.food.find_one({"nfc":long(nfc)})
		date_used = f["Date_Used"] 
		print date_used
		string = string +r["name"] + " Used on: " + date_used.strftime("%m%d%y") +"\n"
	
	r = twiml.Response()
	r.message(string)
	return(str(r))


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
