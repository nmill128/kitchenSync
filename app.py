
import flask
import pymongo
from flask import Flask
from pymongo import MongoClient


app = Flask(__name__)
client = MongoClient()
db = client.newdb


@app.route('/')
def index():
    return "<h1> This flask app is running!<h1>"

@app.route('/Users')
def getUsers():
	 db.users.insert({"name":"Yeomans"})
	 # return db.users.find_one()
	return "HI"

# @app.route('/Trial')
# def getTrial():
# 	return "hi"

# @app.route('/Tester')
# def tryTest():
# 	user = users.find_one()
# 	return "hi"

if __name__=='__main__':
    app.run(port=8000)
