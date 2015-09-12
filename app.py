
import flask
import pymongo
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
	print "Users"
	print db.users
	print "Restock"
	print db.restock.find_one()
	print "Fridge"
	print db.fridge
	print "Stock"
	print db.stock

	return db.restock.find_one()

# @app.route('/Trial')
# def getTrial():
# 	return "hi"

# @app.route('/Tester')
# def tryTest():
# 	user = users.find_one()
# 	return "hi"

if __name__=='__main__':
    app.run(port=8000)
