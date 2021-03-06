
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
from datetime import timedelta
from flask import make_response, current_app
from functools import update_wrapper


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


def crossdomain(origin=None, methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator




#User Counter
Users = 0


def getDate(dt):
	return dt.strftime("%m%d%y")

@app.route('/')
@crossdomain(origin='*')
def index():
	#message = client.sms.messages.create(to=+17038557270, from_=+17038103574,body="Hello there!")
	return redirect("/KenBapp/dashboard", code=302)

@app.route('/<username>/dashboard')
@crossdomain(origin='*')
def userDash(username):
	record = db.users.find_one({"username":username})

	print record
	

	return render_template('dashboard.html',friends=record["Friends"],stock=db.fridge.find({"UserId":('{0:.3g}'.format(record["UserId"]))}),restock=db.restock.find({"UserId":('{0:.3g}'.format(record["UserId"]))}),username=username)

@app.route('/Users')
@crossdomain(origin='*')
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
@crossdomain(origin='*')
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
@crossdomain(origin='*')
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
@crossdomain(origin='*')
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
@crossdomain(origin='*')
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
@crossdomain(origin='*')
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
@crossdomain(origin='*')
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
		price = "{:.2f}".format(data["msrp"])
	elif "saleprice" in data:
		price = "{:.2f}".format(data["salePrice"])
	db.restock.insert({"name":data["name"],"price":price,"upc":record["upc"],"nfc":record["nfc"],"UserId":record["UserId"], "Date_Used":datetime.now()})
	jsonstr = {"name":name, "string":string}
	return json.dumps(jsonstr)

@app.route('/<username>/delete', methods = ["POST"])
@crossdomain(origin='*')
def delete(username):
	nfc = request.form["nfc"]
	# Delete it from the fridge area
	record = db.fridge.find_one({"nfc":nfc})
	db.fridge.remove({"nfc":nfc})
	userrecord = db.users.find_one({"username":username})
	#Add its info to the restock area
	url = "http://api.walmartlabs.com/v1/items?apiKey=jgz3vtvr9cuwguzrzpn54nuy&upc=" + record["upc"]
	contents=urllib2.urlopen(url).read()
	data = json.loads(contents)
	data = data["items"][0]
	price = "N/A"
	if "msrp" in data:
		price = "{:.2f}".format(data["msrp"])
	elif "saleprice" in data:
		price = "{:.2f}".format(data["salePrice"])
	db.restock.insert({"name":data["name"],"price":price,"upc":record["upc"],"nfc":record["nfc"],"UserId":record["UserId"], "Date_Used":datetime.now()})
   	return render_template('kitchenTable.html',stock=db.fridge.find({"UserId":('{0:.3g}'.format(userrecord["UserId"]))}))

@app.route('/<username>/restockLoad', methods = ["GET"])
@crossdomain(origin='*')
def restockLoad(username):
	record = db.users.find_one({"username":username})
   	return render_template('restockTable.html',restock=db.restock.find({"UserId":('{0:.3g}'.format(record["UserId"]))}))

@app.route('/<username>/restockDelete', methods = ["POST"])
@crossdomain(origin='*')
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
@crossdomain(origin='*')
def shareFalse(username):
	userId = request.form["userId"]
	record = db.users.find_one({"username":username})
	db.users.insert({"UserId":userId, "username":record["Username"], "password":record["password"], "name":record["name"], "phone":record["phone"], "sharing":False, "EXPreminders":record["EXPreminders"], "friends":record[friends]})

@app.route('/<username>/addFriend', methods = ["POST"])
@crossdomain(origin='*')
def addFriend(username):
	friendName = request.form["friend"]
	record = db.users.find_one({"username":username})
	fris = []
	if not record["Friends"] == None:
		for fri in record["Friends"]:
			fris.append(fri)
	fris.append(friendName)
	db.users.update({"UserId":record["UserId"]},{"UserId":record["UserId"], "username":record["username"], "Password":record["Password"], "Name":record["Name"], "Phone":record["Phone"], "Sharing":record["Sharing"], "EXPreminders":record["EXPreminders"], "Friends":fris})
   	return render_template('friendTable.html', friends=fris)

@app.route('/<username>/removeFriend', methods = ["POST"])
@crossdomain(origin='*')
def removeFriend(username):
	friendName = request.form["friend"]
	record = db.users.find_one({"username":username})
	fris = []
	if not record["Friends"] == None:
		for fri in record["Friends"]:
			if not fri == friendName:
				fris.append(fri)
	db.users.update({"UserId":record["UserId"]},{"UserId":record["UserId"], "username":record["username"], "Password":record["Password"], "Name":record["Name"], "Phone":record["Phone"], "Sharing":record["Sharing"], "EXPreminders":record["EXPreminders"], "Friends":fris})
   	return render_template('friendTable.html', friends=fris)

@app.route('/<username>/requestFood', methods = ["POST"])
@crossdomain(origin='*')
def requestFood(username):
	nfc = request.form["nfc"]
	sent= False
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
		print UserId
		rec = db.fridge.find_one({"UserId":str(int(UserId)), "upc":foodRecord["upc"]})
		if not rec==None:
			number = "1"+f["Phone"]
			message = client.sms.messages.create(to=+long(number), from_=+17038103574,body="Hello!\n Your friend " + record["Name"]+ " needs " + name)
			sent = True
	if not sent:
		return "None of your friends have " + name+"."
	return "Request Sent"

@app.route('/twilio/sms', methods = ["POST"])
@crossdomain(origin='*')
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
