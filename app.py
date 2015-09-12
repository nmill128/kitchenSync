
import flask
import pymongo
from flask import Flask
from pymongo import MongoClient


app = Flask(__name__)
try:
    client=pymongo.MongoClient()
    print "Connected successfully!!!"
except pymongo.errors.ConnectionFailure, e:
   print "Could not connect to MongoDB: %s" % e 
db = client.newdb


@app.route('/')
def index():
    return "<h1> This flask app is running!<h1>"

@app.route('/Users')
def getUsers():
	print "I'm in the function"
	print client
	 #db.users.insert({"name":"Yeomans"})
	 # return db.users.find_one()
	client.database_names()
	return "turtles"

# @app.route('/Trial')
# def getTrial():
# 	return "hi"

# @app.route('/Tester')
# def tryTest():
# 	user = users.find_one()
# 	return "hi"

if __name__=='__main__':
    app.run(port=8000)
