import os
import json
import bson.json_util
import flask
from flask import Flask
from flask.ext.pymongo import PyMongo
from datetime import datetime,timedelta
import sendgrid
import urllib,urllib2

app = Flask(__name__)
client = MongoClient()


@app.route('/')
def index():
    return "<h1> This flask app is running!<h1>"

@app.route('/Users')
def getUsers():
	return "Hi"

if __name__=='__main__':
    app.run(port=8000)
