
import flask
import pymongo
from flask import Flask
from pymongo import MongoClient


app = Flask(__name__)
client = MongoClient()
users = client.Users_database

@app.route('/')
def index():
    return "<h1> This flask app is running!<h1>"

@app.route('/Users')
def getUsers():
	# return "Hi"
	return users.find_one()

if __name__=='__main__':
    app.run(port=8000)
